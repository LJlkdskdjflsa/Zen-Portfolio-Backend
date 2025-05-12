from typing import Optional, List, Dict, Any, Annotated
from pydantic import BaseModel, HttpUrl, Field, RootModel

class TokenSocials(BaseModel):
    twitter: Optional[str]
    telegram: Optional[str]
    website: Optional[str]

class TokenMeta(BaseModel):
    name: str
    symbol: str
    mint: str
    uri: Optional[str]
    decimals: int
    description: Optional[str]
    image: Optional[str]
    hasFileMetaData: Optional[bool]
    showName: Optional[bool]
    createdOn: Optional[str]
    strictSocials: Optional[Dict[str, str]] = Field(default_factory=dict)
    twitter: Optional[str]
    telegram: Optional[str]
    website: Optional[str]

class PoolSecurity(BaseModel):
    freezeAuthority: Optional[Any]
    mintAuthority: Optional[Any]

class PoolLiquidity(BaseModel):
    quote: float
    usd: float

class PoolPrice(BaseModel):
    quote: float
    usd: float

class PoolMarketCap(BaseModel):
    quote: float
    usd: float

class Pool(BaseModel):
    poolId: str
    liquidity: PoolLiquidity
    price: PoolPrice
    tokenSupply: float
    lpBurn: float
    tokenAddress: str
    marketCap: PoolMarketCap
    market: str
    quoteToken: str
    decimals: int
    security: PoolSecurity
    lastUpdated: Optional[int]
    deployer: Optional[str]
    openTime: Optional[int]
    createdAt: Optional[int]

class EventTimeframe(BaseModel):
    priceChangePercentage: float

class Events(RootModel):
    root: Dict[str, EventTimeframe]

class Risk(BaseModel):
    rugged: bool
    risks: List[Any]
    score: int
    jupiterVerified: bool

class TokenEntry(BaseModel):
    token: TokenMeta
    pools: List[Pool]
    events: Dict[str, EventTimeframe]
    risk: Risk
    buys: int
    sells: int
    txns: int
    holders: int
    balance: float
    value: float

# The top-level DTO for a list of tokens
class TokensResponse(RootModel):
    root: List[TokenEntry]
