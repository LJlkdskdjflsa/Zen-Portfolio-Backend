from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph



import datetime

def generate_portfolio_opportunities(portfolio_data):
    """
    根據 portfolio_data 給出機會建議，回傳指定格式 dict。
    portfolio_data: dict，需包含 walletAddress, totalValue, assets (list of dict)
    每個 asset dict 需包含 name, symbol, amount, value, type (solana/stablecoin/other)
    """
    assets = portfolio_data.get("assets", [])
    total_value = portfolio_data.get("totalValue", 0)
    wallet_address = portfolio_data.get("walletAddress", "")
    generated_at = datetime.datetime.now().isoformat()
    recommendations = []

    # 1. 檢查單一幣種集中度
    if assets:
        sorted_assets = sorted(assets, key=lambda x: x.get("value", 0), reverse=True)
        top_asset = sorted_assets[0]
        top_pct = top_asset.get("value", 0) / total_value * 100 if total_value > 0 else 0
        if top_pct > 70:
            recommendations.append({
                "title": f"Diversify Portfolio by Reducing {top_asset['symbol']} Concentration",
                "description": f"Currently, {top_asset['symbol']} constitutes {top_pct:.1f}% of the portfolio. To mitigate risk, consider reallocating a portion of {top_asset['symbol']} to other promising Solana-based tokens or stablecoins. This will help in reducing the portfolio's vulnerability to {top_asset['symbol']}-specific volatility.",
                "action": f"Reallocate {top_asset['symbol']} Holdings",
                "potentialReturn": "Reduced risk and potential for more stable returns",
                "riskLevel": "Medium",
                "implementationDifficulty": "Medium",
                "timeHorizon": "Immediate"
            })

    # 2. 針對每個資產給機會建議
    for asset in assets:
        symbol = asset.get("symbol")
        asset_type = asset.get("type")
        if asset_type == "solana":
            # Staking
            recommendations.append({
                "title": f"Explore Staking Opportunities for {symbol}",
                "description": f"If {symbol} supports staking, consider staking a portion of your {symbol} holdings to earn passive income. This can provide additional returns while maintaining exposure to {symbol}.",
                "action": f"Stake {symbol} Tokens",
                "potentialReturn": "5-10% annual yield",
                "riskLevel": "Low",
                "implementationDifficulty": "Easy",
                "timeHorizon": "Short-term"
            })
            # DEX流動性
            recommendations.append({
                "title": "Utilize Liquidity Providing on Solana DEXs",
                "description": f"Provide liquidity on decentralized exchanges (DEXs) on the Solana blockchain using a portion of your assets, such as {symbol} and stablecoins. This can generate trading fees and yield farming rewards.",
                "action": "Provide Liquidity",
                "potentialReturn": "Variable APY based on trading volume",
                "riskLevel": "Medium-High",
                "implementationDifficulty": "Advanced",
                "timeHorizon": "Medium-term"
            })
        elif asset_type == "stablecoin":
            # 穩定幣建議
            recommendations.append({
                "title": "Consider Yield Farming or Lending Stablecoins",
                "description": f"Lend or provide liquidity with your stablecoins (e.g., {symbol}) on DeFi protocols to earn yield while maintaining capital stability.",
                "action": "Lend/Provide Liquidity",
                "potentialReturn": "2-8% annual yield",
                "riskLevel": "Low-Medium",
                "implementationDifficulty": "Easy",
                "timeHorizon": "Short-term"
            })

    # 3. 投資新項目
    recommendations.append({
        "title": "Invest in Emerging Solana Projects",
        "description": "Research and invest in emerging projects on the Solana blockchain that have strong fundamentals and growth potential. This can diversify your portfolio and capture early-stage growth.",
        "action": "Research and Invest",
        "potentialReturn": "High potential returns from early-stage investments",
        "riskLevel": "High",
        "implementationDifficulty": "Advanced",
        "timeHorizon": "Long-term"
    })

    # 4. 穩定幣配置建議
    stablecoins = [a for a in assets if a.get("type") == "stablecoin"]
    stablecoin_value = sum(a.get("value", 0) for a in stablecoins)
    if stablecoin_value / total_value < 0.05:
        recommendations.append({
            "title": "Consider Stablecoin Allocation for Stability",
            "description": "Allocate a portion of your portfolio to stablecoins to provide stability and liquidity. This can act as a hedge against market volatility and provide quick access to capital for future opportunities.",
            "action": "Allocate to Stablecoins",
            "potentialReturn": "Stable value with potential for yield farming",
            "riskLevel": "Low",
            "implementationDifficulty": "Easy",
            "timeHorizon": "Immediate"
        })

    return {
        "walletAddress": wallet_address,
        "totalValue": total_value,
        "generatedAt": generated_at,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    # 範例 portfolio 輸入
    example_portfolio = {
        "walletAddress": "3SBfuWVR9cRLaGrHof9eLESeVQcDkUfLf9TRf3nwQTNv",
        "totalValue": 9517.22,
        "assets": [
            {"name": "Zeus Network", "symbol": "ZEUS", "amount": 10000, "value": 9260, "type": "solana"},
            {"name": "Solana", "symbol": "SOL", "amount": 1, "value": 150, "type": "solana"},
            {"name": "USDC", "symbol": "USDC", "amount": 107, "value": 107, "type": "stablecoin"}
        ]
    }
    result = generate_portfolio_opportunities(example_portfolio)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
