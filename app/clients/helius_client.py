import requests
from app.infrastructure.settings import settings
from app.dtos.wallet_total_asset_response_dto import WalletTotalResponseDTO, AssetDTO

def get_wallet_data_by_helius(wallet_address: str) -> WalletTotalResponseDTO:
    """
    Fetch asset data from Helius API and return as a validated DTO.
    """
    url = f"https://mainnet.helius-rpc.com/?api-key={settings.HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "my-id",
        "method": "getAssetsByOwner",
        "params": {
            "ownerAddress": wallet_address,
            "page": 1,
            "limit": 1000,
            "displayOptions": {
                "showFungible": True,
                "showNativeBalance": True
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    result = data.get('result', {})
    items = result.get('items', [])
    native_balance = result.get('nativeBalance', {})
    assets = []
    total_value = 0.0
    # Parse fungible tokens
    for item in items:
        if item.get('interface') == 'FungibleToken' and 'token_info' in item:
            meta = item.get('content', {}).get('metadata', {})
            token_info = item.get('token_info', {})
            price_info = token_info.get('price_info', {})
            image_url = item.get('content', {}).get('links', {}).get('image')
            amount = token_info.get('balance', 0) / (10 ** token_info.get('decimals', 0))
            value = price_info.get('total_price', 0)
            price = price_info.get('price_per_token', 0)
            total_value += value
            assets.append(AssetDTO(
                name=meta.get('name', ''),
                symbol=meta.get('symbol', ''),
                amount=amount,
                value=value,
                percentage=0,  # will be filled later
                tokenId=item.get('id', ''),
                decimals=token_info.get('decimals', 0),
                price=price,
                currency=price_info.get('currency', 'USDC'),
                imageUrl=image_url,
            ))
    # Add native SOL
    if native_balance and native_balance.get('lamports', 0) > 0:
        sol_amount = native_balance['lamports'] / 1_000_000_000
        sol_value = native_balance.get('total_price', 0)
        sol_price = native_balance.get('price_per_sol', 0)
        total_value += sol_value
        assets.append(AssetDTO(
            name="Solana",
            symbol="SOL",
            amount=sol_amount,
            value=sol_value,
            percentage=0,  # will be filled later
            tokenId="SOL",
            decimals=9,
            price=sol_price,
            currency="USDC",
            imageUrl=None,
        ))
    # Calculate percentages
    for asset in assets:
        if total_value > 0:
            asset.percentage = round((asset.value / total_value) * 100, 1)
        else:
            asset.percentage = 0
    # Sort assets by value descending
    assets = sorted(assets, key=lambda x: x.value, reverse=True)
    return WalletTotalResponseDTO(
        address=wallet_address,
        assets=assets,
        totalValue=round(total_value, 2),
    )