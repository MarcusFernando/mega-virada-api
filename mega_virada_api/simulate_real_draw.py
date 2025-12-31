from lottery_logic import analyze_bet

# Drawn numbers from Concurso 2954 (20/12/2025)
DRAWN = [1, 9, 37, 39, 42, 44]

def print_result(title, result):
    print(f"\n--- {title} ---")
    print(f"Meus Números: {result['bet_used']}")
    print(f"Acertos: {result['hits']} ({result['matched_numbers']})")
    p = result['prizes']
    print(f"Prêmios: {p['senas']} Senas, {p['quinas']} Quinas, {p['quadras']} Quadras")

# Scenario 1: Simple Bet (6 nums) hitting Quina
bet1 = [1, 9, 37, 39, 42, 60] # 60 is the miss
res1 = analyze_bet(bet1, DRAWN)
res1['bet_used'] = bet1
print_result("Cenário 1: Aposta Simples (Quina)", res1)

# Scenario 2: 8-Number Bet hitting Quina (The "Multiplier" Effect)
bet2 = [1, 9, 37, 39, 42, 10, 11, 12] # Hits 1, 9, 37, 39, 42 (5 hits)
res2 = analyze_bet(bet2, DRAWN)
res2['bet_used'] = bet2
print_result("Cenário 2: Aposta de 8 Nums (Quina)", res2)

# Scenario 3: Real Life "Bad Luck" (2 hits)
bet3 = [1, 2, 3, 4, 37, 60]
res3 = analyze_bet(bet3, DRAWN)
res3['bet_used'] = bet3
print_result("Cenário 3: Azar (Só 2 acertos)", res3)
