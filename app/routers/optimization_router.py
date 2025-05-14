from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx

from app.dtos.optimization_dto import OptimizationResponse, OptimizationResponseWithTx, OptimizationAction
from app.services.asset_opportunity_graph_script import generate_solana_optimization_suggestions

router = APIRouter(
    prefix="/optimization",
    tags=["optimization"],
    responses={404: {"description": "Not found"}},
)


class SolanaAssetsRequest(BaseModel):
    """Request model for Solana asset optimization."""
    assets: List[Dict[str, Any]]


@router.post("/solana", response_model=OptimizationResponseWithTx)
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
        optimization_response = generate_solana_optimization_suggestions(assets=request.assets)

        symbol_to_mint = {
            "SOL": "So11111111111111111111111111111111111111112",
            "JITOSOL": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",
            "Highest APY Yield Pool": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn"
        }

        # replace symbol with mint address
        for action in optimization_response.optimization_actions:
            if action.input_mint in symbol_to_mint:
                action.input_mint = symbol_to_mint[action.input_mint]
            if action.output_mint in symbol_to_mint:
                action.output_mint = symbol_to_mint[action.output_mint]

        # get action tx data
        # get quote from each action
        # get swap tx data        
        tx_data = []
        async with httpx.AsyncClient(timeout=10) as client:
            for action in optimization_response.optimization_actions:
                # Jupiter expects amount as integer string (usually in smallest units, e.g. lamports for SOL)
                # Here, we assume amount is already correct. If not, conversion is needed.
                params = {
                    "inputMint": action.input_mint,
                    "outputMint": action.output_mint,
                    "amount": str(int(action.amount * 1e9)),
                }
                try:
                    resp = await client.get(
                        "https://lite-api.jup.ag/swap/v1/quote",
                        params=params,
                        headers={"Accept": "application/json"}
                    )
                    quote_json = resp.json() if resp.status_code == 200 else {"error": resp.text}
                except Exception as ex:
                    quote_json = {"error": str(ex)}
                tx_data.append({
                    "action": action.dict(),
                    "quote": quote_json
                })
        
        optimization_response_with_tx = OptimizationResponseWithTx(
            wallet_score=optimization_response.wallet_score,
            wallet_total_suggestion=optimization_response.wallet_total_suggestion,
            recommendations_list=optimization_response.recommendations_list,
            optimization_actions=optimization_response.optimization_actions,
            tx_data=tx_data
        )

        return optimization_response_with_tx
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate optimization suggestions: {str(e)}"
        )
