from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from app.enums.chain_enum import ChainEnum

class AssetDTO(BaseModel):
    name: str
    symbol: str
    amount: float
    value: float
    percentage: float
    tokenId: str
    decimals: int
    price: float
    currency: str
    imageUrl: Optional[HttpUrl] = None

class WalletTotalResponseDTO(BaseModel):
    chain: ChainEnum
    address: str
    assets: List[AssetDTO]
    totalValue: float
