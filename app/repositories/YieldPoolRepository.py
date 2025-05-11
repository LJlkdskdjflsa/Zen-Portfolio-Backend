from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

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
        # rewardTokens and underlyingTokens are already in the correct format for the database
        # No conversion needed for JSON fields as SQLAlchemy with JSON column type handles this
            
        # Extract prediction data if available
        if 'predictions' in pool_data and pool_data['predictions'] is not None:
            predictions = pool_data.pop('predictions')
            pool_data['predictedClass'] = predictions.get('predictedClass')
            pool_data['predictedProb'] = predictions.get('predictedProbability')
            pool_data['binnedConfidence'] = predictions.get('binnedConfidence')
        
        # Create new yield pool record
        yield_pool = YieldPool(**pool_data)
        self.db.add(yield_pool)
        self.db.flush()  # Flush to get the ID without committing
        
        return yield_pool
    
    def create_many(self, pools: List[Dict[str, Any]]) -> int:
        """
        Create multiple yield pool records in the database
        
        Args:
            pools: List of dictionaries containing yield pool data
            
        Returns:
            Number of records created
        """
        created_count = 0
        
        for pool_data in pools:
            self.create_yield_pool(pool_data)
            created_count += 1
            
        return created_count
    
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
