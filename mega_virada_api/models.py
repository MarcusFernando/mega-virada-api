from pydantic import BaseModel, Field, validator
from typing import List, Optional

class BetScenario(BaseModel):
    selected_numbers: List[int] = Field(..., description="List of numbers in the bet (6 to 20)")
    drawn_numbers: List[int] = Field(..., description="List of 6 drawn numbers")

    @validator('selected_numbers')
    def validate_bet_size(cls, v):
        if not (6 <= len(v) <= 20):
            raise ValueError('Bet must have between 6 and 20 numbers')
        if len(set(v)) != len(v):
            raise ValueError('Bet numbers must be unique')
        return v
    
    @validator('drawn_numbers')
    def validate_drawn_size(cls, v):
        if len(v) != 6:
            raise ValueError('Draw must consist of exactly 6 numbers')
        return v

class PrizeResult(BaseModel):
    senas: int
    quinas: int
    quadras: int
    total_awards: int

class SimulationResponse(BaseModel):
    matches_count: int
    matched_numbers: List[int]
    prizes: PrizeResult
    message: str

class ConferirBolaoRequest(BaseModel):
    drawn_numbers: List[int]
    bets: List[List[int]]
    sena_prize: float = 0.0
    quina_prize: float = 0.0
    quadra_prize: float = 0.0
    num_shares: int = 1

class BetResult(BaseModel):
    bet_index: int
    numbers_played: int
    matched_numbers: List[int]
    matches_count: int
    prizes: PrizeResult

class BolaoSummary(BaseModel):
    total_senas: int
    total_quinas: int
    total_quadras: int
    total_prize_value: float
    value_per_share: float
    details: List[BetResult]
    summary_text: str
