from typing import List, Literal, Dict, Any
from pydantic import BaseModel, Field

class OptimizationRecommendation(BaseModel):
    """Model for optimization recommendations."""
    title: str
    description: str
    action: str
    potentialReturn: str
    riskLevel: str
    implementationDifficulty: str
    timeHorizon: str

class OptimizationAction(BaseModel):
    """Optimization action , including input mint, output mint and amount, user can swap."""
    input_mint: str = Field(..., description="Input mint (token mint address), e.g: So11111111111111111111111111111111111111112")
    output_mint: str = Field(..., description="Output mint (token mint address), e.g: J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn")
    amount: float = Field(..., description="Amount")
    optimization_action_detail: str = Field(..., description="Optimization action detail, e.g. swap 0.01 SOL to JITOSOL to get more yield")

class SolanaAssetsRequest(BaseModel):
    assets: List[Dict[str, Any]]
    optimization_actions: List[OptimizationAction]
    
class OptimizationResponse(BaseModel):
    """Model for the complete optimization response."""
    wallet_score: Literal["A", "B", "C", "D", "F"]
    wallet_total_suggestion: str
    recommendations_list: List[OptimizationRecommendation]
    optimization_actions: List[OptimizationAction]

class OptimizationResponseWithTx(OptimizationResponse):
    """Model for the complete optimization response."""
    tx_data: List[Dict[str, Any]]