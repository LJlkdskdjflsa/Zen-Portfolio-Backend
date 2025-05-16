from app.dtos.wallet_total_asset_response_dto import WalletTotalResponseDTO, AssetDTO
from moralis import evm_api
from app.infrastructure.settings import settings
from app.enums.chain_enum import ChainEnum

def get_wallet_data_by_moralis(wallet_address: str, chain: ChainEnum = ChainEnum.BASE) -> WalletTotalResponseDTO:
    params = {
        "address": wallet_address,
        "chain": chain.value,
    }
    result = evm_api.wallets.get_wallet_token_balances_price(
        api_key=settings.MORALIS_API_KEY,
        params=params,
    )
    assets = []
    total_value = 0.0
    tokens = result.get('result', [])
    for token in tokens:
        name = token.get("name", "")
        symbol = token.get("symbol", "")
        amount = float(token.get("balance", 0)) / (10 ** int(token.get("decimals", 0) or 0))
        value = float(token.get("usd_value") or 0)
        price = float(token.get("usd_price") or 0)
        token_id = token.get("token_address") or token.get("address") or ""
        decimals = int(token.get("decimals", 0) or 0)
        currency = "USD"
        image_url = token.get("logo") or token.get("thumbnail") or None
        total_value += value
        assets.append(AssetDTO(
            name=name,
            symbol=symbol,
            amount=amount,
            value=value,
            percentage=0,  # will be filled later
            tokenId=token_id,
            decimals=decimals,
            price=price,
            currency=currency,
            imageUrl=image_url,
        ))
    # Calculate percentages
    for asset in assets:
        if total_value > 0:
            asset.percentage = round((asset.value / total_value) * 100, 1)
        else:
            asset.percentage = 0
    # Sort by value descending
    assets = sorted(assets, key=lambda x: x.value, reverse=True)
    return WalletTotalResponseDTO(
        address=wallet_address,
        assets=assets,
        totalValue=round(total_value, 2),
        chain=chain,
    )