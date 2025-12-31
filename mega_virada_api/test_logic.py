
from lottery_logic import analyze_bet

def test_scenario_a():
    # Cenário A: 28 apostas simples (simulation logic handled mentally by user, but let's check simple bet logic)
    # User says: 1 bet of 6 numbers. Hit 5 numbers.
    bet = [1, 2, 3, 4, 5, 6]
    drawn = [1, 2, 3, 4, 5, 10] # Hit 1-5
    
    result = analyze_bet(bet, drawn)
    print("--- Cenário A (Simples, 5 acertos) ---")
    print(f"Hits: {result['hits']}")
    print(f"Prizes: {result['prizes']}")
    # Expected: 1 Quina (and 0 Quadras because you need 4 hits, but 5 hits implies the lower tier logic isn't additive for simple bets usually? 
    # WAIT. Simple bet rules: 5 hits = Quina prize ONLY. You don't get Quadra prize on top for the same ticket unless it's a multiple bet decomposition.
    # Our logic uses the combinatorial formula which works for Simple bets too:
    # Bet 6, Hit 5:
    # Senas: C(5,6)*... = 0
    # Quinas: C(5,5)*C(1,1) = 1 * 1 = 1. Correct.
    # Quadras: C(5,4)*C(1,2) = 5 * 0 = 0. Correct. (C(1,2) is 0)
    
def test_scenario_b():
    # Cenário B: 1 aposta de 8 números. Hit 5 numbers.
    # User expects: 3 Quinas e 15 Quadras.
    bet = [1, 2, 3, 4, 5, 6, 7, 8]
    drawn = [1, 2, 3, 4, 5, 60] # Hit 1,2,3,4,5
    
    result = analyze_bet(bet, drawn)
    print("\n--- Cenário B (8 números, 5 acertos) ---")
    print(f"Hits: {result['hits']}")
    print(f"Prizes: {result['prizes']}")
    
    expected_quinas = 3
    expected_quadras = 15
    
    assert result['prizes']['quinas'] == expected_quinas, f"Expected {expected_quinas} Quinas, got {result['prizes']['quinas']}"
    assert result['prizes']['quadras'] == expected_quadras, f"Expected {expected_quadras} Quadras, got {result['prizes']['quadras']}"
    print("SUCCESS: Matches User Expectation!")

if __name__ == "__main__":
    test_scenario_a()
    test_scenario_b()
