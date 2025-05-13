from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.dtos.optimization_dto import OptimizationResponse
from app.services.asset_opportunity_graph_script import generate_solana_optimization_suggestions

router = APIRouter(
    prefix="/optimization",
    tags=["optimization"],
    responses={404: {"description": "Not found"}},
)


class SolanaAssetsRequest(BaseModel):
    """Request model for Solana asset optimization."""
    assets: List[Dict[str, Any]]


@router.post("/solana", response_model=OptimizationResponse)
async def optimize_solana_assets(request: SolanaAssetsRequest):
    """
    Generate optimization suggestions for Solana assets.
    
    This endpoint analyzes the provided assets and returns personalized optimization
    recommendations including wallet score and suggested actions.
    
    Args:
        request: SolanaAssetsRequest containing the user's asset list
        
    Returns:
        OptimizationResponse with wallet score and recommendations
    """
    try:
        return generate_solana_optimization_suggestions(assets=request.assets)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate optimization suggestions: {str(e)}"
        )
