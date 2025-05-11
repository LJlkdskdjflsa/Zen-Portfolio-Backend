from typing import TypedDict, List, Dict, Any
from data.input.mock_asset_data import mock_asset_data
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field
import enum
from langchain_openai import ChatOpenAI
from app.infrastructure.settings import settings
from langchain_core.language_models.chat_models import BaseChatModel

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




# Example asset list (replace with your real asset data source)
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


def assets_router(state):

    # Entry node: pass all assets to next steps
    model_with_structure = get_langchain_model().with_structured_output(AssetList)

    
    prompt = "As a financial advisor, please analyze the following assets and return a list of assets" + str(state)
    # Invoke the model
    structured_output = model_with_structure.invoke(
        input=prompt
    )
    
    

    return {"assets": structured_output}

def filter_solana(state):
    solana_assets = [a for a in state["assets"] if a["type"] == "solana"]
    return {"solana_assets": solana_assets}


def filter_stablecoin(state):
    stablecoin_assets = [a for a in state["assets"] if a["type"] == "stablecoin"]
    return {"stablecoin_assets": stablecoin_assets}


def find_solana_opportunity(state):
    opportunities = [
        {"asset": a, "opportunity": "Stake on Solana"}
        for a in state.get("solana_assets", [])
    ]
    return {"solana_opportunities": opportunities}


def find_stablecoin_opportunity(state):
    opportunities = [
        {"asset": a, "opportunity": "Lend on Aave"}
        for a in state.get("stablecoin_assets", [])
    ]
    return {"stablecoin_opportunities": opportunities}


if __name__ == "__main__":
    # Build the graph
    workflow = StateGraph(AssetState)

    workflow.add_node("A", assets_router)

    # workflow.add_node("B", filter_solana)
    # workflow.add_node("C", filter_stablecoin)
    # workflow.add_node("D", find_solana_opportunity)
    # workflow.add_node("E", find_stablecoin_opportunity)

    # workflow.add_edge("A", "B")
    # workflow.add_edge("A", "C")
    # workflow.add_edge("B", "D")
    # workflow.add_edge("C", "E")

    workflow.set_entry_point("A")

    app = workflow.compile()
    result = app.invoke({"assets": mock_asset_data.get("assets")})

    print(result)
