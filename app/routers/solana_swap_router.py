from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from app.dtos.optimization_dto import OptimizationAction

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}},
)


class SolanaQuoteSwapRequest(BaseModel):
    action: OptimizationAction
    userPublicKey: str


class SolanaQuoteSwapResponse(BaseModel):
    # quote: dict
    transaction: str


@router.post("/solana", response_model=SolanaQuoteSwapResponse)
async def get_solana_quote_and_swap(request: SolanaQuoteSwapRequest):
    """
    Given an optimization action and user public key, return the quote and swap transaction data.
    """
    action = request.action
    async with httpx.AsyncClient(timeout=15) as client:
        params = {
            "inputMint": action.input_mint,
            "outputMint": action.output_mint,
            "amount": str(int(action.amount * 1e9)),
        }
        # 1. Get quote
        try:
            resp = await client.get(
                "https://lite-api.jup.ag/swap/v1/quote",
                params=params,
                headers={"Accept": "application/json"},
            )
            quote_json = (
                resp.json() if resp.status_code == 200 else {"error": resp.text}
            )
        except Exception as ex:
            quote_json = {"error": str(ex)}

        # 2. Get swap transaction using the quote (if valid)
        swap_tx_json = None
        if quote_json and not quote_json.get("error"):
            swap_payload = {
                "userPublicKey": request.userPublicKey,
                "quoteResponse": quote_json,
                "prioritizationFeeLamports": {
                    "priorityLevelWithMaxLamports": {
                        "maxLamports": 10000000,
                        "priorityLevel": "veryHigh",
                    }
                },
                "dynamicComputeUnitLimit": True,
            }
            try:
                swap_resp = await client.post(
                    "https://lite-api.jup.ag/swap/v1/swap",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json=swap_payload,
                )
                swap_tx_json = (
                    swap_resp.json()
                    if swap_resp.status_code == 200
                    else {"error": swap_resp.text}
                )
            except Exception as swap_ex:
                swap_tx_json = {"error": str(swap_ex)}
        else:
            swap_tx_json = {"error": "No valid quote for swap"}

    return SolanaQuoteSwapResponse(transaction=swap_tx_json.get("swapTransaction"))
