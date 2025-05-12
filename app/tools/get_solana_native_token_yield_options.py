from langchain_core.tools import tool
from sqlalchemy import select, or_
from app.infrastructure.database import get_db_context
from app.models.YieldPool import YieldPool
from pydantic import BaseModel, Field
from typing import Optional, List


class YieldPoolDTO(BaseModel):
    """Data Transfer Object for Yield Pool information"""
    # pool_id: str = Field(..., description="Unique identifier for the yield pool")
    chain: str = Field(..., description="Blockchain chain name")
    project: str = Field(..., description="Project name")
    pool: str = Field(..., description="Pool name")
    symbol: str = Field(..., description="Token symbol")
    tvlUsd: Optional[float] = Field(None, description="Total value locked")
    apy: Optional[float] = Field(None, description="Annual percentage yield")
    apyBase: Optional[float] = Field(None, description="Base annual percentage yield")
    url: Optional[str] = Field(None, description="External link to the pool")
    rewards_tokens: Optional[List[str]] = Field(None, description="List of reward tokens")
    risk_level: Optional[str] = Field(None, description="Risk level of the pool")
    
    class Config:
        from_attributes = True


@tool(parse_docstring=True)
def get_solana_native_token_yield_options() -> list[YieldPoolDTO]:
    """
    Retrieve yield options for Solana native token (SOL) from the database.
    Will return yield pools of Solana native token with TVL of 10 million USD or more.

    Returns:
        list: A list of yield pools related to Solana native token
    """

    # Construct query based on the SQL:
    # SELECT * FROM public.yield_pools
    # WHERE chain = 'Solana' AND (
    #   symbol ILIKE '%SOL%' OR
    #   project ILIKE '%SOL%' OR
    #   pool ILIKE '%SOL%'
    # )
    with get_db_context() as db:
        SOL_PATTERN = "%SOL%"
        query = select(YieldPool).where(
            YieldPool.chain == "Solana",
            or_(
                YieldPool.symbol.ilike(SOL_PATTERN),
            ),
            # Exclude liquidity pools (symbols containing "-")
            ~YieldPool.symbol.like("%-%"),
            # Only include pools with TVL of 10 million USD or more
            YieldPool.tvlUsd >= 10000000
        )
        
        result = db.execute(query)
        solana_yield_options = result.scalars().all()
        
        # Convert ORM objects to YieldPoolDTO instances and return
        return [
            YieldPoolDTO.model_validate(pool)
            for pool in solana_yield_options
        ]
