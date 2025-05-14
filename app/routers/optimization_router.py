# This router only contains the optimization suggestion endpoint.
# For swap/quote logic, see solana_swap_router.py

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.dtos.optimization_dto import OptimizationResponse, OptimizationAction
from app.services.asset_opportunity_graph_script import (
    generate_solana_optimization_suggestions,
)

router = APIRouter(
    prefix="/optimization",
    tags=["optimization"],
    responses={404: {"description": "Not found"}},
)


class SolanaAssetsRequest(BaseModel):
    """Request model for Solana asset optimization."""

    assets: List[Dict[str, Any]]
    walletAddress: str  # Still included for compatibility, but not used here


@router.post("/solana", response_model=OptimizationResponse)
async def optimize_solana_assets(request: SolanaAssetsRequest):
    """
    Generate optimization suggestions for Solana assets.
    Returns wallet score, total suggestion, recommendations, and optimization actions only.
    """
    try:
        optimization_response = generate_solana_optimization_suggestions(
            assets=request.assets
        )

        symbol_to_mint = {
            "SOL": "So11111111111111111111111111111111111111112",
            "JITOSOL": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",
            "Highest APY Yield Pool": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",
        }

        # replace symbol with mint address
        for action in optimization_response.optimization_actions:
            if action.input_mint in symbol_to_mint:
                action.input_mint = symbol_to_mint[action.input_mint]
            if action.output_mint in symbol_to_mint:
                action.output_mint = symbol_to_mint[action.output_mint]

        return optimization_response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate optimization suggestions: {str(e)}",
        )
