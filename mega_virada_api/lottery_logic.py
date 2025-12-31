import math
from typing import List, Tuple

def nCr(n, r):
    if r < 0 or r > n:
        return 0
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))

def calculate_split_prizes(numbers_in_bet: int, hits: int) -> Tuple[int, int, int]:
    """
    Calculates the breakdown of prizes (Senas, Quinas, Quadras) for a single multiple bet.
    Formula: C(H, k) * C(N-H, 6-k)
    where N = numbers in bet, H = hits, k = prize tier requirements (6, 5, 4)
    """
    if hits < 4:
        return 0, 0, 0
        
    # Senas (k=6)
    senas = nCr(hits, 6) * nCr(numbers_in_bet - hits, 6 - 6)
    
    # Quinas (k=5)
    quinas = nCr(hits, 5) * nCr(numbers_in_bet - hits, 6 - 5)
    
    # Quadras (k=4)
    quadras = nCr(hits, 4) * nCr(numbers_in_bet - hits, 6 - 4)
    
    return senas, quinas, quadras

def analyze_bet(bet: List[int], drawn: List[int]):
    """
    Analyzes a single bet against the drawn numbers.
    """
    bet_set = set(bet)
    drawn_set = set(drawn)
    matched = bet_set.intersection(drawn_set)
    hits = len(matched)
    
    senas, quinas, quadras = calculate_split_prizes(len(bet), hits)
    
    return {
        "matched_numbers": list(matched),
        "hits": hits,
        "prizes": {
            "senas": senas,
            "quinas": quinas,
            "quadras": quadras,
            "total_awards": senas + quinas + quadras
        }
    }
