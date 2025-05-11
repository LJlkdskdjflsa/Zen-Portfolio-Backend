from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Boolean
import datetime

from app.utils.database_util import DBBase

class YieldPool(DBBase):
    """
    Model for yield pool data from DeFi Llama API
    """
    __tablename__ = "yield_pools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chain = Column(String, nullable=False)
    project = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    tvlUsd = Column(Float, nullable=False)
    apyBase = Column(Float, nullable=True)
    apyReward = Column(Float, nullable=True)
    apy = Column(Float, nullable=False)
    # Additional APY fields from DeFi Llama
    apyPct1D = Column(Float, nullable=True)
    apyPct7D = Column(Float, nullable=True)
    apyPct30D = Column(Float, nullable=True)
    stablecoin = Column(Boolean, nullable=True)
    rewardTokens = Column(JSON, nullable=True)
    pool = Column(String, nullable=False)
    underlyingTokens = Column(JSON, nullable=True)
    ilRisk = Column(String, nullable=True)
    exposure = Column(String, nullable=True)
    predictedClass = Column(String, nullable=True)
    predictedProb = Column(Float, nullable=True)
    binnedConfidence = Column(Float, nullable=True)
    url = Column(String, nullable=True)
    volumeUsd1d = Column(Float, nullable=True)
    volumeUsd7d = Column(Float, nullable=True)
    # Additional fields for metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<YieldPool(id={self.id}, chain='{self.chain}', project='{self.project}', symbol='{self.symbol}')>"
