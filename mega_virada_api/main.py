from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import BetScenario, SimulationResponse, ConferirBolaoRequest, BolaoSummary, BetResult, PrizeResult
from lottery_logic import analyze_bet

app = FastAPI(title="Mega da Virada API", description="API para simulação e conferência de bolões da Mega Sena")

# Mount Frontend (Serve HTML/CSS/JS)
app.mount("/site", StaticFiles(directory="frontend", html=True), name="site")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/simular-premio", response_model=SimulationResponse)
def simular_premio(scenario: BetScenario):
    """
    Simulates a result for a specific bet scenario.
    """
    result = analyze_bet(scenario.selected_numbers, scenario.drawn_numbers)
    
    prizes = result["prizes"]
    msg_parts = []
    if prizes["senas"] > 0:
        msg_parts.append(f"{prizes['senas']} Sena(s)")
    if prizes["quinas"] > 0:
        msg_parts.append(f"{prizes['quinas']} Quina(s)")
    if prizes["quadras"] > 0:
        msg_parts.append(f"{prizes['quadras']} Quadra(s)")
        
    summary_text = ", ".join(msg_parts) if msg_parts else "Nenhum prêmio"
    
    return SimulationResponse(
        matches_count=result["hits"],
        matched_numbers=result["matched_numbers"],
        prizes=PrizeResult(**prizes),
        message=f"Resultado: {summary_text}"
    )

@app.post("/conferir-bolao", response_model=BolaoSummary)
def conferir_bolao(request: ConferirBolaoRequest):
    """
    Checks multiple bets against a draw and returns the consolidated result for the pool.
    """
    total_senas = 0
    total_quinas = 0
    total_quadras = 0
    bet_results = []
    
    for idx, bet in enumerate(request.bets):
        # Basic validation per bet provided in list
        if not (6 <= len(bet) <= 20):
            # skipping invalid logs or could raise error. For robust API, maybe return error per bet?
            # For simplicity, we process valid ones or let it fail? 
            # Let's assume valid as per broad types, but logic handles it.
            pass
            
        res = analyze_bet(bet, request.drawn_numbers)
        p = res["prizes"]
        
        total_senas += p["senas"]
        total_quinas += p["quinas"]
        total_quadras += p["quadras"]
        
        bet_results.append(BetResult(
            bet_index=idx + 1,
            numbers_played=len(bet),
            matched_numbers=res["matched_numbers"],
            matches_count=res["hits"],
            prizes=PrizeResult(**p)
        ))
        
    summary_parts = []
    if total_senas > 0: summary_parts.append(f"{total_senas} Sena(s)")
    if total_quinas > 0: summary_parts.append(f"{total_quinas} Quina(s)")
    if total_quadras > 0: summary_parts.append(f"{total_quadras} Quadra(s)")
    
    # Financial Calculation
    total_value = (total_senas * request.sena_prize) + \
                  (total_quinas * request.quina_prize) + \
                  (total_quadras * request.quadra_prize)
    
    val_per_share = total_value / request.num_shares if request.num_shares > 0 else 0
    
    header = "BOLÃO DA EMPRESA - RESULTADO"
    prize_text = f"Premiação Total: {', '.join(summary_parts) if summary_parts else 'Nenhum prêmio'}"
    money_text = f"Valor Total: R$ {total_value:,.2f} | Por Cota: R$ {val_per_share:,.2f}"
    
    final_text = f"{header}\n{prize_text}\n{money_text}"
    
    return BolaoSummary(
        total_senas=total_senas,
        total_quinas=total_quinas,
        total_quadras=total_quadras,
        total_prize_value=total_value,
        value_per_share=val_per_share,
        details=bet_results,
        summary_text=final_text
    )

# --- Statistical Module Endpoints ---
from stats_logic import get_stats, generate_smart_game

@app.get("/estatisticas")
def get_statistics():
    """
    Returns historical statistics of Mega Sena.
    """
    return get_stats()

@app.post("/gerar-jogo-inteligente")
def gerar_jogo_inteligente(strategy: str = "equilibrada", quantity: int = 6):
    """
    Generates a game based on a strategy: 'quentes', 'atrasados', 'equilibrada', 'surpresinha'.
    Quantity: 6 to 15 numbers.
    """
    game = generate_smart_game(strategy, quantity)
    return {"strategy": strategy, "quantity": quantity, "game": game}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

