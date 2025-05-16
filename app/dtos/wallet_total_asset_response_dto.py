from typing import List, Optional
from pydantic import BaseModel, HttpUrl

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
    address: str
    assets: List[AssetDTO]
    totalValue: float
