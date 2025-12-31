const API_URL = "";

function openTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

function parseNumbers(inputStr) {
    // Splits by space, comma, or newline and filters empty strings
    return inputStr.split(/[\s,]+/).filter(x => x).map(Number);
}

// --- Simulator Logic ---
async function simularPremio() {
    const betInput = document.getElementById('sim-bet').value;
    const drawInput = document.getElementById('sim-draw').value;
    const resultBox = document.getElementById('sim-result');

    try {
        const bet = parseNumbers(betInput);
        const draw = parseNumbers(drawInput);

        if (bet.length < 6 || draw.length !== 6) {
            alert("Verifique os números. A aposta deve ter no mínimo 6 e o sorteio deve ter exatamente 6.");
            return;
        }

        const response = await fetch(`${API_URL}/simular-premio`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected_numbers: bet, drawn_numbers: draw })
        });

        if (!response.ok) throw new Error("Erro na API");

        const data = await response.json();

        resultBox.classList.remove('hidden');
        resultBox.innerHTML = `
            <div class="result-detail">Acertos: <span class="highlight">${data.matches_count}</span></div>
            <div class="result-detail" style="margin-top:10px; border-top:1px solid #333; padding-top:10px;">
                ${formatPrizeLine(data.prizes)}
            </div>
            <div class="result-detail" style="color: #bbb; font-size: 0.9em; margin-top: 5px;">
                ${data.message}
            </div>
        `;

    } catch (e) {
        alert("Erro ao conectar com a API: " + e.message);
    }
}

// --- Pool Checker Logic (with Quotas) ---
async function conferirBolao() {
    const drawInput = document.getElementById('bol-draw').value;
    const betsInput = document.getElementById('bol-bets').value.trim().split("\n");

    // Financial Inputs
    const prizeSena = parseFloat(document.getElementById('prize-sena').value) || 0;
    const prizeQuina = parseFloat(document.getElementById('prize-quina').value) || 0;
    const prizeQuadra = parseFloat(document.getElementById('prize-quadra').value) || 0;
    const numShares = parseInt(document.getElementById('num-shares').value) || 1;

    const resultBox = document.getElementById('bol-result');

    try {
        const draw = parseNumbers(drawInput);
        const bets = betsInput.map(line => parseNumbers(line)).filter(b => b.length >= 6);

        if (draw.length !== 6) {
            alert("O sorteio deve ter 6 números.");
            return;
        }

        if (bets.length === 0) {
            alert("Insira pelo menos um jogo válido.");
            return;
        }

        const payload = {
            drawn_numbers: draw,
            bets: bets,
            sena_prize: prizeSena,
            quina_prize: prizeQuina,
            quadra_prize: prizeQuadra,
            num_shares: numShares
        };

        const response = await fetch(`${API_URL}/conferir-bolao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Erro na API");

        const data = await response.json();

        resultBox.classList.remove('hidden');

        const winners = data.details.filter(d => d.matches_count >= 4);

        let detailsHtml = "";
        if (winners.length > 0) {
            detailsHtml = "<h4>Jogos Premiados:</h4>";
            winners.forEach(w => {
                detailsHtml += `<div style="margin-bottom:5px;">
                    Jogo ${w.bet_index} (${w.numbers_played} nums): <span class="highlight">${w.matches_count} Acertos</span>
                 </div>`;
            });
        } else {
            detailsHtml = "<p>Nenhum jogo premiado nesta simulação.</p>";
        }

        // Financial Display
        const moneyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
        const totalMoney = moneyFormatter.format(data.total_prize_value);
        const shareMoney = moneyFormatter.format(data.value_per_share);

        resultBox.innerHTML = `
            <div style="background:#0a3d1b; padding:10px; border-radius:8px; margin-bottom:15px; border:1px solid #20913f;">
                <div style="font-size:1.2rem; margin-bottom:5px;">PRÊMIO TOTAL: <span class="highlight">${totalMoney}</span></div>
                <div style="font-size:1.1rem;">POR COTA (${numShares}): <span class="highlight">${shareMoney}</span></div>
            </div>

            <h2 style="color:var(--accent); margin-top:0;">${data.total_senas} SENA(S)</h2>
            <div class="result-detail">Total Quinas: <span class="highlight">${data.total_quinas}</span></div>
            <div class="result-detail">Total Quadras: <span class="highlight">${data.total_quadras}</span></div>
            <hr style="border-color:#333">
            ${detailsHtml}
        `;

    } catch (e) {
        alert("Erro ao processar: " + e.message);
    }
}

function formatPrizeLine(prizes) {
    let parts = [];
    if (prizes.senas) parts.push(`<div>${prizes.senas} x Sena</div>`);
    if (prizes.quinas) parts.push(`<div>${prizes.quinas} x Quina</div>`);
    if (prizes.quadras) parts.push(`<div>${prizes.quadras} x Quadra</div>`);

    if (parts.length === 0) return "Sem prêmios :(";
    return parts.join("");
}

// --- Statistical Module Logic ---
async function carregarEstatisticas() {
    const listHot = document.getElementById('list-hot');
    const listDelayed = document.getElementById('list-delayed');

    // Only load if empty (cache logic simpler for UI)
    if (listHot.innerHTML !== "Carregando...") return;

    try {
        const response = await fetch(`${API_URL}/estatisticas`);
        if (!response.ok) throw new Error("Erro ao carregar");
        const data = await response.json();

        // Render Hot
        listHot.innerHTML = data.most_common.map((item, index) =>
            `<li>
                <span>#${index + 1} <b>Dezena ${item.number}</b></span>
                <span class="stat-badge">${item.count}x</span>
             </li>`
        ).join("");

        // Render Delayed
        listDelayed.innerHTML = data.most_delayed.map((item, index) =>
            `<li>
                <span>#${index + 1} <b>Dezena ${item.number}</b></span>
                <span class="stat-badge">${item.delay} jogos</span>
             </li>`
        ).join("");

    } catch (e) {
        listHot.innerHTML = "Erro ao carregar.";
    }
}

// --- Generator Logic ---
async function gerarJogo() {
    const strategy = document.getElementById('strategy').value;
    const quantity = document.getElementById('quantity').value;
    const resultBox = document.getElementById('gen-result');
    const numbersSpan = document.getElementById('gen-numbers');

    try {
        const response = await fetch(`${API_URL}/gerar-jogo-inteligente?strategy=${strategy}&quantity=${quantity}`, {
            method: 'POST'
        });
        const data = await response.json();

        resultBox.classList.remove('hidden');
        numbersSpan.innerText = data.game.join(" - ");
    } catch (e) {
        alert("Erro ao gerar jogo.");
    }
}

// --- Planner Logic ---
async function planejarBolao() {
    const shareValue = parseFloat(document.getElementById('plan-share-value').value) || 0;
    const shares = parseInt(document.getElementById('plan-shares').value) || 0;
    const resultBox = document.getElementById('plan-result');

    if (shareValue <= 0 || shares <= 0) {
        alert("Por favor, preencha valor e cotas.");
        return;
    }

    const totalBudget = shareValue * shares;

    // Cost constants (Dec 2025) - Mega Sena
    const COST_6 = 5.00;
    const COST_7 = 35.00;
    const COST_8 = 140.00;
    const COST_9 = 420.00;

    // Strategy Logic (Maximize 8, then 7, then 6)
    let remaining = totalBudget;
    let games9 = 0; // Added support for 9 because why not?
    let games8 = 0;
    let games7 = 0;
    let games6 = 0;

    // Logic: If budget is high (>2000), buy a 9.
    while (remaining >= COST_9 && remaining > 2000) {
        games9++;
        remaining -= COST_9;
    }

    while (remaining >= COST_8) {
        games8++;
        remaining -= COST_8;
    }

    while (remaining >= COST_7) {
        games7++;
        remaining -= COST_7;
    }

    while (remaining >= COST_6) {
        games6++;
        remaining -= COST_6;
    }

    const change = remaining;
    resultBox.innerHTML = "<p><i>Gerando palpites inteligentes, aguarde...</i></p>";
    resultBox.classList.remove('hidden');

    // Helper to generate games HTML
    const generateBlock = async (count, size, cost) => {
        if (count === 0) return "";
        let html = `<li style="background:#222; padding:15px; margin:5px 0; border-left:4px solid var(--accent); border-radius:4px;">
            <div style="font-size:1.1rem; color:#fff; margin-bottom:10px;">
                🔥 <b>${count} Jogos de ${size} Dezenas</b>
                <span style="float:right; font-size:0.9rem; color:#888;">${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(count * cost)}</span>
            </div>
            <div style="font-family:monospace; color:#4caf50;">`;

        for (let i = 0; i < count; i++) {
            // Strategy variation: Mix strategies for variety
            const strategies = ['equilibrada', 'quentes', 'surpresinha'];
            const strat = strategies[i % strategies.length];

            const resp = await fetch(`${API_URL}/gerar-jogo-inteligente?strategy=${strat}&quantity=${size}`, { method: 'POST' });
            const data = await resp.json();
            html += `<div style="padding:5px 0; border-bottom:1px solid #333;">${data.game.join(" - ")} <span style="color:#666; font-size:0.8rem;">(${strat})</span></div>`;
        }

        html += `</div></li>`;
        return html;
    };

    // Generate blocks
    const block9 = await generateBlock(games9, 9, COST_9);
    const block8 = await generateBlock(games8, 8, COST_8);
    const block7 = await generateBlock(games7, 7, COST_7);
    const block6 = await generateBlock(games6, 6, COST_6);

    const moneyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

    resultBox.innerHTML = `
        <h3>Estratégia Gerada</h3>
        <p>Orçamento Total: <span class="highlight">${moneyFormatter.format(totalBudget)}</span></p>
        
        <ul style="list-style:none; padding:0;">
            ${block9}
            ${block8}
            ${block7}
            ${block6}
        </ul>
        
        <p style="text-align:right; color:#888;">Troco estimado: ${moneyFormatter.format(change)}</p>
    `;
}

