from typing import TypedDict, List, Dict, Any
from data.input.mock_asset_data import mock_asset_data
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
import enum
import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from app.infrastructure.settings import settings
from langchain_core.language_models.chat_models import BaseChatModel
from app.infrastructure.database import get_db_context
from app.repositories.YieldPoolRepository import YieldPoolRepository


class AssetTypeEnum(str, enum.Enum):
    """Asset type enum.

    SOLANA: Solana native token (SOL)
    STABLECOIN: Stablecoin (USDC, USDT, etc.)
    MEME_TOKEN: Meme tokens, like TRUMP, DOGE, etc.
    YIELD_BEARING_TOKEN: Yield bearing tokens (e.g. Aave, Compound)
    LIQUIDITY_STAKING_TOKEN: Liquidity staking tokens (e.g. MSOL, JUPSOL, JITOSOL...)
    OTHER: Other assets

    """

    SOLANA = "solana"
    STABLECOIN = "stablecoin"
    MEME_TOKEN = "meme_token"
    YIELD_BEARING_TOKEN = "yield_bearing_token"
    LIQUIDITY_STAKING_TOKEN = "liquidity_staking_token"
    OTHER = "other"

    # NFT = "nft"


class AssetState(TypedDict, total=False):
    assets: List[Dict[str, Any]]
    solana_assets: List[Dict[str, Any]]
    stablecoin_assets: List[Dict[str, Any]]
    solana_opportunities: List[Dict[str, Any]]
    stablecoin_opportunities: List[Dict[str, Any]]


class Asset(BaseModel):
    """Asset model."""

    type: AssetTypeEnum
    symbol: str
    amount: float
    value: float
    percentage: float
    tokenId: str = Field(..., alias="tokenId")
    decimals: int
    price: float
    currency: str
    imageUrl: str | None = None


class AssetList(BaseModel):
    assets: List[Asset]


class OptimizationRecommendation(BaseModel):
    """Model for optimization recommendations."""

    title: str
    description: str
    action: str
    potentialReturn: str
    riskLevel: str
    implementationDifficulty: str
    timeHorizon: str


class OptimizationResponse(BaseModel):
    """Model for the complete optimization response."""

    walletAddress: str
    totalValue: float
    generatedAt: str
    recommendations: List[OptimizationRecommendation]


def get_langchain_model() -> BaseChatModel:
    model = ChatOpenAI(
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=settings.OPENAI_API_KEY,
    )
    return model


def get_solana_staking_options():
    """
    Get all Solana staking options from the database.

    Returns:
        List of yield pool data for Solana staking options
    """
    try:
        with get_db_context() as db:
            repo = YieldPoolRepository(db)
            # Get all yield pools for Solana chain with a minimum APY of 1%
            solana_pools = repo.get_all(chain="solana", min_apy=1.0)

            # Convert SQLAlchemy objects to dictionaries
            result = []
            for pool in solana_pools:
                pool_dict = {
                    "chain": pool.chain,
                    "project": pool.project,
                    "symbol": pool.symbol,
                    "tvlUsd": pool.tvlUsd,
                    "apy": pool.apy,
                    "apyBase": pool.apyBase,
                    "apyReward": pool.apyReward,
                    "stablecoin": pool.stablecoin,
                    "ilRisk": pool.ilRisk,
                    "exposure": pool.exposure,
                    "url": pool.url,
                }
                result.append(pool_dict)

            return result
    except Exception as e:
        print(f"Error fetching Solana staking options: {str(e)}")
        return []


def generate_solana_optimization_suggestions(assets: list[dict]):
    """
    Generate optimization suggestions for Solana assets.

    Args:
        assets: List of user assets
        wallet_address: User's wallet address
        total_value: Total value of the portfolio

    Returns:
        Optimization response with recommendations
    """
    # Get Solana staking options from the database
    # solana_staking_options = get_solana_staking_options()

    # Create a model with structured output for optimization recommendations
    model = get_langchain_model().with_structured_output(AssetList)

    # Prepare the prompt with asset data and staking options
    prompt = f"""
    As a financial advisor specializing in Solana assets, and give me user assets list.
    
    User's assets:
    {json.dumps(assets, indent=2)}
    """

    # Generate the optimization response
    optimization_response = model.invoke(input=prompt)

    return optimization_response


def get_optimization_suggestion_from_profile(state):
    """
    Generate optimization suggestions based on the user's asset profile.

    Args:
        state: Current state containing asset information

    Returns:
        Updated state with optimization suggestions
    """

    # Generate optimization suggestions for Solana assets
    optimization_response = generate_solana_optimization_suggestions(
        assets=state
    )

    # Return the updated state with optimization suggestions
    return optimization_response 

if __name__ == "__main__":
    # Build the graph
    workflow = StateGraph(AssetState)

    workflow.add_node("A", get_optimization_suggestion_from_profile)
    workflow.set_entry_point("A")
    workflow.add_edge("A", END)

    app = workflow.compile()
    result = app.invoke(mock_asset_data)

    # Extract the optimization suggestions
    solana_opportunities = result.get("solana_opportunities", {})

    # Save the optimization suggestions to a JSON file
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "optimizationOutput.json")

    with open(output_file, "w") as f:
        json.dump(solana_opportunities, f, indent=2)

    print(f"Optimization suggestions saved to {output_file}")
    print(json.dumps(solana_opportunities, indent=2))
