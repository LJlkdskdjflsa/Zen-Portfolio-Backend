from typing import TypedDict, List, Dict, Any, Literal
from cachetools import TTLCache, cached
import hashlib
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




# Create LRU cache for 10 minutes (600 seconds), maxsize 128 (adjust as needed)
llm_cache = TTLCache(maxsize=128, ttl=600)

def _assets_hash(assets: list[dict]) -> str:
    # Create a hash of the assets input for cache key
    assets_str = json.dumps(assets, sort_keys=True)
    return hashlib.sha256(assets_str.encode('utf-8')).hexdigest()

@cached(llm_cache, key=lambda assets: _assets_hash(assets))
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
    As a financial advisor specializing in Solana assets, and give me user assets list.
    
    User's assets:"""
        + json.dumps(asset_list_dto.model_dump(), indent=2)
        + """
    
    # if the amount of SOL is more than 0.005 SOL, suggest staking to the highest APY yield pool
    # if the amount of STABLECOIN is more than 100USD total, suggest staking to the highest APY yield pool
    # if the amount of YIELD_BEARING_TOKEN is more than 100USD total, suggest staking to the highest APY yield pool
    # if the amount of LIQUIDITY_STAKING_TOKEN is more than 100USD total, suggest staking to the highest APY yield pool
    # if the amount of OTHER is more than 100USD total, suggest staking to the highest APY yield pool


    # SOL mint address: So11111111111111111111111111111111111111112
    # Jitosol mint address: J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn
    
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

    example:
    
    user_amount: 0.05 SOL
    
    optimization_actions:
    - input_mint: So11111111111111111111111111111111111111112
    - output_mint: J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn
    - amount: 0.01 SOL
    - optimization_action_detail: swap 0.01 SOL to JITOSOL to get more yield

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
