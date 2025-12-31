from collections import Counter
import random
from history_loader import get_all_draws

# Total Mega Sena numbers
ALL_NUMBERS = range(1, 61)

def get_stats():
    draws = get_all_draws()
    total_draws = len(draws)
    
    # Flatten all numbers
    all_drawn_numbers = []
    last_appearance = {n: -1 for n in ALL_NUMBERS}
    
    for draw in draws:
        concurso = draw['concurso']
        for num in draw['dezenas']:
            all_drawn_numbers.append(num)
            last_appearance[num] = concurso
            
    # Frequencies
    counter = Counter(all_drawn_numbers)
    most_common = counter.most_common(10) # Top 10
    least_common = counter.most_common()[:-11:-1] # Bottom 10
    
    # Atrasados (Current Draw - Last Seen Draw)
    # Careful: We need the LATEST draw number safely
    latest_concurso = draws[-1]['concurso'] if draws else 0
    
    atrasos = []
    for n in ALL_NUMBERS:
        if last_appearance[n] == -1:
            atraso = latest_concurso # Never seen (unlikely)
        else:
            atraso = latest_concurso - last_appearance[n]
        atrasos.append({"number": n, "delay": atraso})
    
    # Sort by delay descending
    atrasos.sort(key=lambda x: x['delay'], reverse=True)
    top_atrasados = atrasos[:10]
    
    return {
        "total_draws": total_draws,
        "most_common": [{"number": n, "count": c} for n, c in most_common],
        "least_common": [{"number": n, "count": c} for n, c in least_common],
        "most_delayed": top_atrasados
    }

def generate_smart_game(strategy: str, quantity: int = 6):
    if quantity < 6 or quantity > 15:
        quantity = 6 # Safe fallback
        
    stats = get_stats()
    
    hot_numbers = [item['number'] for item in stats['most_common']] 
    # Use more hot numbers if needed for larger games
    if len(hot_numbers) < quantity:
         # Extend with more common numbers if top 10 is not enough
         # For simplicity here, we re-fetch with larger limit or just use current list + random
         hot_numbers = [item['number'] for item in stats['most_common']] # logic holds for now as we have few strategies
    
    cold_numbers = [item['number'] for item in stats['least_common']]
    delayed_numbers = [item['number'] for item in stats['most_delayed']]
    
    # Strategy Logic
    game = set()
    
    if strategy == "quentes":
        # Mix of mostly hot numbers
        # If quantity is large (e.g. 15), we need more candidates.
        # Let's take top 20 hot if needed
        # Since get_stats returns top 10, we might need to rely on fill-logic for >10 size or improve get_stats
        # For now, let's fill with available hot + random
        candidates = hot_numbers + delayed_numbers[:5]
        game.update(random.sample(candidates, k=min(quantity, len(candidates))))
        
    elif strategy == "atrasados":
        candidates = delayed_numbers
        game.update(random.sample(candidates, k=min(quantity, len(candidates))))
        
    elif strategy == "equilibrada":
        # Proportional split?
        # 1/3 Hot, 1/3 Delayed, 1/3 Random
        n_part = quantity // 3
        game.update(random.sample(hot_numbers, k=min(len(hot_numbers), n_part)))
        game.update(random.sample(delayed_numbers, k=min(len(delayed_numbers), n_part)))
        
    elif strategy == "surpresinha":
        game.update(random.sample(ALL_NUMBERS, k=quantity))
        
    # Fill if missing (fallback)
    while len(game) < quantity:
        missing = quantity - len(game)
        leftover = list(set(ALL_NUMBERS) - game)
        game.update(random.sample(leftover, k=missing))
    
    # Return sorted list
    return sorted(list(game))
