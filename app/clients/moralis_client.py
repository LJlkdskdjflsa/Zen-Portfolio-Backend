from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from moralis import evm_api
from app.infrastructure.settings import settings
from typing import Optional, List, Dict, Any

def get_wallet_token_balances_price(wallet_address: str, chain: str = "base") -> Dict[str, Any]:
    params = {
                "address": wallet_address,
                "chain": chain,
            }
    result = evm_api.wallets.get_wallet_token_balances_price(
                api_key=settings.MORALIS_API_KEY,
                params=params,
            )
    return TokenBalanceResponse(**result)