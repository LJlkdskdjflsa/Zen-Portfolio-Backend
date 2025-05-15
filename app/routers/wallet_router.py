from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from moralis import evm_api
from app.infrastructure.settings import settings
from typing import Optional, List, Dict, Any

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"],
    responses={404: {"description": "Not found"}},
)

class TokenBalanceResponse(BaseModel):
    block_number: int
    cursor: Optional[str]
    page: int
    page_size: int
    result: List[Dict[str, Any]]

@router.get("/{wallet_address}/token-balances", response_model=TokenBalanceResponse)
async def get_wallet_token_balances(
    wallet_address: str,
    chain: str = "base"
) -> TokenBalanceResponse:
    """
    Get token balances with prices for a specific wallet address.
    
    Args:
        wallet_address: The wallet address to query
        chain: The blockchain chain to query (default: base)
    
    Returns:
        TokenBalanceResponse: Token balances with price information
    """
    try:
        params = {
            "address": wallet_address,
            "chain": chain,
        }
        
        result = evm_api.wallets.get_wallet_token_balances_price(
            api_key=settings.MORALIS_API_KEY,
            params=params,
        )
        
        return TokenBalanceResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch wallet token balances: {str(e)}"
        )
