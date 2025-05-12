from typing import TypedDict, List, Dict, Any, Literal
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
from app.tools.get_solana_native_token_yield_options import (
    get_solana_native_token_yield_options,
)
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from app.clients.llm_model_client import get_llm_model


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

    wallet_score: Literal["A", "B", "C", "D", "F"]
    wallet_total_suggestion: str
    recommendations_list: List[OptimizationRecommendation]





def generate_solana_optimization_suggestions(assets: list[dict]) -> OptimizationResponse:
    """
    Generate optimization suggestions for Solana assets using LangChain's tool calling to produce an OptimizationResponse.

    Args:
        assets: List of user assets

    Returns:
        OptimizationResponse with recommendations
    """
    # Use LangChain model with structured output for OptimizationResponse
    llm = get_llm_model()
    # Prepare the prompt with detailed rules for the LLM
    prompt = f"""
    As a financial advisor specializing in Solana assets, and give me user assets list.
    
    User's assets:
    {json.dumps(assets, indent=2)}
    """

    # Generate the optimization response
    asset_list_dto = llm.with_structured_output(AssetList).invoke(input=prompt)

    prompt = (
        """
    As a financial advisor specializing in Solana assets, and give me user assets list.
    
    User's assets:"""
        + json.dumps(asset_list_dto.model_dump(), indent=2)
        + """
    
    # if the amount of SOL is more than 0.5 SOL, suggest staking to the highest APY yield pool
    # if the amount of MEME token is more than 100USD total, tell the user not gambling, make can deposit some to JLP or MSOL these kind of nice assets
    # if the amount of STABLECOIN is more than 100USD total, suggest staking to the highest APY yield pool
    # if the amount of YIELD_BEARING_TOKEN is more than 100USD total, suggest staking to the highest APY yield pool
    # if the amount of LIQUIDITY_STAKING_TOKEN is more than 100USD total, suggest staking to the highest APY yield pool
    # if the amount of OTHER is more than 100USD total, suggest staking to the highest APY yield pool
    """
    )

    tools = [
        Tool(
            name="get_solana_native_token_yield_options",
            func=get_solana_native_token_yield_options,
            description="""
        Get yield options for Solana native token (SOL) from the database.
        Will return yield pools of Solana native token with TVL of 10 million USD or more.
        """,
        ),
    ]

    # Create an agent
    financial_suggestion_string = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True
    ).run(prompt)

    prompt = """
    These are the user's assets:
    """+json.dumps(assets, indent=2)+"""
    And these are the advice from the previous step:
    """+financial_suggestion_string+"""
    please help to suggest some optimization suggestions, within the format of OptimizationResponse.
    """

    financial_suggestion_dto = llm.with_structured_output(OptimizationResponse).invoke(
        input=prompt
    )

    return financial_suggestion_dto


def get_optimization_suggestion_from_profile(state):
    """
    Generate optimization suggestions based on the user's asset profile.

    Args:
        state: Current state containing asset information

    Returns:
        Updated state with optimization suggestions
    """

    # Generate optimization suggestions for Solana assets
    optimization_response = generate_solana_optimization_suggestions(assets=state)

    # Return the updated state with optimization suggestions
    return optimization_response


if __name__ == "__main__":
    # Build the graph
    workflow = StateGraph(AssetState)

    workflow.add_node("A", get_optimization_suggestion_from_profile)
    workflow.set_entry_point("A")
    workflow.add_edge("A", END)

    app = workflow.compile()
    # result = app.invoke(mock_asset_data)
    result = generate_solana_optimization_suggestions(assets=mock_asset_data)

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
