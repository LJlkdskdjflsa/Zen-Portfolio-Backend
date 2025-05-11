from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.models.YieldPool import YieldPool

class YieldPoolRepository:
    """
    Repository for handling YieldPool data operations
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize repository with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        
    def create_yield_pool(self, pool_data: Dict[str, Any]) -> YieldPool:
        """
        Create a new yield pool record in the database
        
        Args:
            pool_data: Dictionary containing yield pool data
            
        Returns:
            Created YieldPool instance
        """
        # Filter out keys that are not part of the YieldPool model
        valid_keys = {
            'chain', 'project', 'symbol', 'tvlUsd', 'apyBase', 'apyReward', 'apy',
            'apyPct1D', 'apyPct7D', 'apyPct30D', 'stablecoin', 'rewardTokens', 'pool',
            'underlyingTokens', 'ilRisk', 'exposure', 'url', 'volumeUsd1d', 'volumeUsd7d'
        }
        
        # Remove any extra keys not in the model
        filtered_pool_data = {k: v for k, v in pool_data.items() if k in valid_keys}
        
        # Extract prediction data if available
        if 'predictions' in pool_data and pool_data['predictions'] is not None:
            predictions = pool_data['predictions']
            filtered_pool_data['predictedClass'] = predictions.get('predictedClass')
            filtered_pool_data['predictedProb'] = predictions.get('predictedProbability')
            filtered_pool_data['binnedConfidence'] = predictions.get('binnedConfidence')
        
        # Create new yield pool record
        yield_pool = YieldPool(**filtered_pool_data)
        self.db.add(yield_pool)
        self.db.flush()  # Flush to get the ID without committing
        
        return yield_pool
    
    def create_many(self, pools: List[Dict[str, Any]]) -> int:
        """
        Create multiple yield pool records in the database
        
        Args:
            pools: List of pool data dictionaries
        
        Returns:
            Number of pools created
        """
        created_pools = []
        for pool_data in pools:
            try:
                created_pool = self.create_yield_pool(pool_data)
                created_pools.append(created_pool)
            except Exception as e:
                # Log the error for the specific pool but continue processing other pools
                logging.error(f"Error creating pool: {pool_data}. Error: {str(e)}")
        
        self.db.commit()
        return len(created_pools)
    
    def get_all(self, 
                chain: Optional[str] = None,
                project: Optional[str] = None,
                min_tvl: Optional[float] = None,
                min_apy: Optional[float] = None) -> List[YieldPool]:
        """
        Get all yield pools with optional filtering
        
        Args:
            chain: Filter by blockchain chain
            project: Filter by project name
            min_tvl: Minimum TVL in USD
            min_apy: Minimum APY percentage
            
        Returns:
            List of YieldPool instances
        """
        query = self.db.query(YieldPool)
        
        if chain:
            query = query.filter(YieldPool.chain == chain)
            
        if project:
            query = query.filter(YieldPool.project.ilike(f"%{project}%"))
            
        if min_tvl is not None:
            query = query.filter(YieldPool.tvlUsd >= min_tvl)
            
        if min_apy is not None:
            query = query.filter(YieldPool.apy >= min_apy)
            
        return query.all()
    
    def get_by_id(self, pool_id: int) -> Optional[YieldPool]:
        """
        Get a yield pool by its ID
        
        Args:
            pool_id: The ID of the pool to retrieve
            
        Returns:
            YieldPool instance if found, None otherwise
        """
        return self.db.query(YieldPool).filter(YieldPool.id == pool_id).first()
    
    def delete_all(self) -> int:
        """
        Delete all yield pools
        
        Returns:
            Number of records deleted
        """
        return self.db.query(YieldPool).delete()
