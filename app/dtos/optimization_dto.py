from typing import List, Literal
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

class OptimizationResponse(BaseModel):
    """Model for the complete optimization response."""
    wallet_score: Literal["A", "B", "C", "D", "F"]
    wallet_total_suggestion: str
    recommendations_list: List[OptimizationRecommendation]
