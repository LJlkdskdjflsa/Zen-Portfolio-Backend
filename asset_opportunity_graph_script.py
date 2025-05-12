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


# Example asset list (replace with your real asset data source)

def get_solana_optimization_suggestions_for_wallet(wallet_address: str) -> dict:
    """
    Generate Solana optimization suggestions for a given wallet address.
    Looks up the user's assets and total value, calls the optimization engine,
    and returns the result as a dict matching the required JSON format.

    Args:
        wallet_address: The Solana wallet address.
    Returns:
        dict: Optimization suggestions in the specified format.
    """
    # For demonstration, use mock_asset_data. Replace with DB lookup in production.
    from data.input.mock_asset_data import mock_asset_data
    if mock_asset_data.get("walletAddress") != wallet_address:
        raise ValueError(f"No mock data for wallet address {wallet_address}")
    assets = mock_asset_data.get("assets", [])
    total_value = mock_asset_data.get("totalValue", 0)

    result = generate_solana_optimization_suggestions(assets, wallet_address, total_value)
    # If result is a Pydantic model, convert to dict
    if hasattr(result, 'dict'):
        result = result.dict()
    return result

# Usage example (for test or integration):
# suggestions = get_solana_optimization_suggestions_for_wallet("3SBfuWVR9cRLaGrHof9eLESeVQcDkUfLf9TRf3nwQTNv")
# print(json.dumps(suggestions, indent=2))

def get_assets():
    return [
        {"type": "solana", "name": "SOL"},
        {"type": "stablecoin", "name": "USDC"},
        {"type": "solana", "name": "MSOL"},
        {"type": "stablecoin", "name": "USDT"},
    ]


def get_langchain_model()->BaseChatModel:
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
                    "url": pool.url
                }
                result.append(pool_dict)
            
            return result
    except Exception as e:
        print(f"Error fetching Solana staking options: {str(e)}")
        return []


def generate_solana_optimization_suggestions(assets, wallet_address, total_value):
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
    solana_staking_options = get_solana_staking_options()
    
    # Create a model with structured output for optimization recommendations
    model = get_langchain_model().with_structured_output(OptimizationResponse)
    
    # Generate current timestamp in ISO format
    current_time = datetime.utcnow().isoformat() + "Z"
    
    # Prepare the prompt with asset data and staking options
    prompt = f"""
    As a financial advisor specializing in Solana assets, please analyze the following portfolio and generate optimization recommendations.
    
    User's wallet address: {wallet_address}
    Total portfolio value: ${total_value}
    
    User's assets:
    {json.dumps(assets, indent=2)}
    
    Available Solana staking options:
    {json.dumps(solana_staking_options, indent=2)}
    
    Based on this information, generate a comprehensive optimization strategy for this portfolio.
    Focus on:
    1. Portfolio diversification
    2. Risk management
    3. Yield optimization through staking
    4. Liquidity considerations
    5. Long-term growth potential
    
    Return the recommendations in a structured format with the following fields:
    - walletAddress: The user's wallet address (use: {wallet_address})
    - totalValue: The total portfolio value (use: {total_value})
    - generatedAt: Current timestamp in ISO format (use: {current_time})
    - recommendations: A list of 5 specific recommendations, each with:
      - title: A concise title for the recommendation
      - description: Detailed explanation of the recommendation
      - action: The specific action to take
      - potentialReturn: Estimated return (can be a range or percentage)
      - riskLevel: Low, Medium, or High
      - implementationDifficulty: Easy, Medium, or Advanced
      - timeHorizon: Immediate, Short-term, Medium-term, or Long-term
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
    # Extract assets from state
    assets = state.get("assets", [])
    
    # Get wallet address and total value from mock data
    # In a real application, this would come from the state or user input
    wallet_address = mock_asset_data.get("walletAddress")
    total_value = mock_asset_data.get("totalValue")
    
    # Generate optimization suggestions for Solana assets
    optimization_response = generate_solana_optimization_suggestions(
        assets, wallet_address, total_value
    )
    
    # Return the updated state with optimization suggestions
    return {
        "assets": assets,
        "solana_opportunities": optimization_response.dict()
    }




if __name__ == "__main__":
    # Build the graph
    workflow = StateGraph(AssetState)

    workflow.add_node("A", get_optimization_suggestion_from_profile)
    workflow.set_entry_point("A")
    workflow.add_edge("A", END)

    app = workflow.compile()
    result = app.invoke({"assets": mock_asset_data.get("assets")})

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
