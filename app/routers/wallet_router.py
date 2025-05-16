from fastapi import APIRouter, HTTPException
from app.utils.address_util import is_evm_address, is_solana_address
from app.clients.solana_tracker_client import get_wallet_data_by_solana_tracker
from fastapi import status
from app.dtos.token_balance_response_dto import TokenBalanceResponse
from app.clients.moralis_client import get_wallet_token_balances_price

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{wallet_address}/token-balances", response_model=TokenBalanceResponse)
async def get_wallet_token_balances(wallet_address: str) -> TokenBalanceResponse:
    """
    Get token balances with prices for a specific wallet address (Base or Solana).
    The address type is auto-detected.
    """
    try:
        if is_evm_address(wallet_address):
            result = get_wallet_token_balances_price(wallet_address=wallet_address, chain="base")
            return result

        elif is_solana_address(wallet_address):
            solana_tokens = get_wallet_data_by_solana_tracker(wallet_address)
            # Normalize to TokenBalanceResponse
            # block_number, cursor, page, page_size are not meaningful for Solana, set defaults
            token_list = []
            for entry in solana_tokens.root:
                token_list.append(
                    {
                        "name": entry.token.name,
                        "symbol": entry.token.symbol,
                        "mint": entry.token.mint,
                        "balance": entry.balance,
                        "value": entry.value,
                        "decimals": entry.token.decimals,
                        "image": entry.token.image,
                    }
                )
            return TokenBalanceResponse(
                block_number=0,
                cursor=None,
                page=1,
                page_size=len(token_list),
                result=token_list,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet address format.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch wallet token balances: {str(e)}",
        )
