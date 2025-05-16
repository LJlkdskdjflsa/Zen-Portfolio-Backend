from fastapi import APIRouter, HTTPException
from app.utils.address_util import is_evm_address, is_solana_address
from fastapi import status
from app.clients.moralis_client import get_wallet_data_by_moralis
from app.clients.helius_client import get_wallet_data_by_helius
from app.dtos.wallet_total_asset_response_dto import WalletTotalResponseDTO
from app.enums.chain_enum import ChainEnum

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{wallet_address}/token-balances", response_model=WalletTotalResponseDTO)
async def get_wallet_token_balances(wallet_address: str) -> WalletTotalResponseDTO:
    """
    Get token balances with prices for a specific wallet address (Base or Solana).
    The address type is auto-detected.
    """
    try:
        if is_evm_address(wallet_address):
            result = get_wallet_data_by_moralis(wallet_address=wallet_address, chain=ChainEnum.BASE)
            return result

        elif is_solana_address(wallet_address):
            # Use the new Helius-based function and return the new API format directly
            solana_assets = get_wallet_data_by_helius(wallet_address)
            return solana_assets
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
