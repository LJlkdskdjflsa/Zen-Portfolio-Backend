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
from app.dtos.optimization_dto import OptimizationAction, OptimizationResponse


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




def generate_solana_optimization_suggestions(
    assets: list[dict],
) -> OptimizationResponse:
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
    get_asset_list_prompt = f"""
    As a financial advisor specializing in Solana assets, and give me user assets list.
    
    User's assets:
    {json.dumps(assets, indent=2)}
    """

    # Generate the optimization response
    asset_list_dto = llm.with_structured_output(AssetList).invoke(input=get_asset_list_prompt)

    # Improved, explicit prompt for the LLM
    get_optimization_advice_prompt = (
        """
You are a financial advisor specializing in Solana assets. Your job is to analyze the user's asset list and provide optimization suggestions in the format of an OptimizationResponse.

The OptimizationResponse must include:
- wallet_score: Rate the overall health of the user's portfolio ('A', 'B', 'C', 'D', or 'F').
- wallet_total_suggestion: A summary of your main advice.
- recommendations_list: A list of optimization advice. Each item should include:
    - title, description, action, potentialReturn, riskLevel, implementationDifficulty, timeHorizon.
- optimization_actions: A list of actions the user can take to improve their yield. Each action must include:
    - input_mint, output_mint, amount, optimization_action_detail.

Rules for optimization_actions:
1. If the user holds SOL and the amount is greater than 0.04 SOL:
    - Suggest staking exactly (user_SOL_amount - 0.04) SOL to the highest APY yield pool.
    - The amount field must be (user_SOL_amount - 0.04), rounded to 9 decimals.
    - The optimization_action_detail must match the amount and say:
      "Stake {amount} SOL to the highest APY yield pool for better returns."
    - Always leave 0.04 SOL for gas fees.
2. If the user has 0.04 SOL or less, do not suggest any staking or swapping actions for SOL.
3. Do not suggest multiple staking actions for SOL; only one solid action is needed.
4. If there are other tokens with clear yield opportunities, apply similar logic: always leave enough for gas and match the amount and detail fields.
5. Do not suggest gambling or high-risk actions.

Format your response as valid JSON matching the OptimizationResponse schema.

User's assets:
"""
        + json.dumps(asset_list_dto.model_dump(), indent=2)
        + """

Previous advice (if any):
"""
        + financial_suggestion_string
        + """
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
    ).run(get_optimization_advice_prompt)

    get_optimization_advice_prompt = (
        """
    These are the user's assets:
    """
        + json.dumps(assets, indent=2)
        + """
    And these are the advice from the previous step:
    """
        + financial_suggestion_string
        + """
    please help to suggest some optimization suggestions, within the format of OptimizationResponse.

        ---
    Need to return OptimizationResponse
    
    OptimizationResponse:
    recommendations_list -> list of optimization advice
    
    optimization_actions -> give the swap action for user to swap some assets to other assets to get more yield (just give solid advice, don't give too many actions. if there are solana native token yield options, suggest to stake some solana native token to the highest APY yield pool)
    (the amount of optimization_actions should still have some room for gas fee, 0.04 SOL is needed for gas fee), so if the user has less than 0.04 SOL, and didn't have any yield options, don't suggest to swap
    if the user has less than 0.04 SOL, and have yield options, suggest to stake some solana native token to the highest APY yield pool
    the amount of optimization_actions is user_amount - 0.04 SOL
    """
    )

    financial_suggestion_dto = llm.with_structured_output(OptimizationResponse).invoke(
        input=get_optimization_advice_prompt
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
