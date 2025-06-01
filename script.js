// script.js

// --- Local Game State ---
const localGameState = {
    hand_ids: [],
    discard_ids: [],
    location1_ids: [],
    location2_ids: [],
    location3_ids: [],
    // Deck is not managed on frontend for this version, backend uses default and filters.
};

// --- Card Data (for display purposes - ideally fetched or preloaded) ---
// This is a simplified version. A real app would fetch this from backend or have it preloaded.
// For now, we'll just use IDs. The backend has the full card data.
const cardManifest = {
    // Main Deck
    1: { name: 'Blade' }, 2: { name: 'Gambit' }, 3: { name: 'Corvus Glaive' },
    4: { name: 'Jubilee' }, 5: { name: 'Ghost Rider' }, 6: { name: 'Blink' },
    7: { name: 'Legion' }, 8: { name: 'Infinity Ultron' }, 9: { name: 'Gorr' },
    10: { name: 'Hela' }, 11: { name: 'Odin' }, 12: { name: 'The Infinaut' },
    // Ultron Stones
    101: { name: 'Mind Stone' }, 102: { name: 'Power Stone' }, 103: { name: 'Reality Stone' },
    104: { name: 'Soul Stone' }, 105: { name: 'Space Stone' }, 106: { name: 'Time Stone' }
};

// --- UI Update Functions ---
function getZoneName(zoneId) {
    if (zoneId === 'hand') return 'Mão';
    if (zoneId === 'location1') return 'Local 1';
    if (zoneId === 'location2') return 'Local 2';
    if (zoneId === 'location3') return 'Local 3';
    if (zoneId === 'discard') return 'Descarte';
    return 'Zone';
}

function renderZone(zoneId) {
    const cardListDiv = document.getElementById(`${zoneId}CardList`);
    const countSpan = document.getElementById(`${zoneId}Count`);
    if (!cardListDiv || !countSpan) return;

    cardListDiv.innerHTML = ''; // Clear current cards
    const ids_key = `${zoneId}_ids`; // e.g. hand_ids, location1_ids

    localGameState[ids_key].forEach((cardId, index) => {
        const cardName = cardManifest[cardId] ? cardManifest[cardId].name : `ID Desconhecido: ${cardId}`;
        const cardItem = document.createElement('span');
        cardItem.className = 'card-item';
        cardItem.textContent = cardName;

        // Add a remove button for each card
        const removeButton = document.createElement('button');
        removeButton.textContent = 'x';
        removeButton.style.marginLeft = '5px';
        removeButton.style.cursor = 'pointer';
        removeButton.onclick = () => removeCardFromZone(zoneId, index);
        cardItem.appendChild(removeButton);

        cardListDiv.appendChild(cardItem);
    });
    countSpan.textContent = localGameState[ids_key].length;
}

function addCardToZone(zoneId) {
    const cardIdInput = document.getElementById('cardIdInput');
    const cardId = parseInt(cardIdInput.value);

    if (isNaN(cardId) || !cardManifest[cardId]) {
        alert('Por favor, insira um ID de carta válido.');
        return;
    }

    const ids_key = `${zoneId}_ids`;
    const zoneName = getZoneName(zoneId);

    // Prevent adding too many cards to locations
    if (zoneId.startsWith('location') && localGameState[ids_key].length >= 4) {
        alert(`O ${zoneName} já tem 4 cartas.`);
        return;
    }

    localGameState[ids_key].push(cardId);
    renderZone(zoneId);
    cardIdInput.value = ''; // Clear input
}

function removeCardFromZone(zoneId, cardIndexInZone) {
    const ids_key = `${zoneId}_ids`;
    if (cardIndexInZone >= 0 && cardIndexInZone < localGameState[ids_key].length) {
        localGameState[ids_key].splice(cardIndexInZone, 1);
        renderZone(zoneId);
    }
}


// --- Event Listener for Analyze Button ---
document.getElementById('analyzeButton').addEventListener('click', async () => {
    const resultsOutputDiv = document.getElementById('analysisResultsOutput');
    resultsOutputDiv.innerHTML = '<p>Analisando... Por favor, aguarde.</p>';

    const currentTurn = parseInt(document.getElementById('currentTurn').value);
    const currentEnergy = parseInt(document.getElementById('currentEnergy').value);
    const maxEnergy = parseInt(document.getElementById('maxEnergy').value);

    if (isNaN(currentTurn) || isNaN(currentEnergy) || isNaN(maxEnergy)) {
        resultsOutputDiv.innerHTML = '<p style="color: red;">Erro: Turno ou Energia inválidos.</p>';
        return;
    }

    const payload = {
        hand_ids: localGameState.hand_ids,
        discard_ids: localGameState.discard_ids,
        location1_ids: localGameState.location1_ids,
        location2_ids: localGameState.location2_ids,
        location3_ids: localGameState.location3_ids,
        current_turn: currentTurn,
        current_energy: currentEnergy,
        max_energy: maxEnergy
    };

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Erro desconhecido ao processar resposta do servidor." }));
            throw new Error(`Erro do servidor: ${response.status} ${response.statusText}. Detalhes: ${errorData.detail || 'N/A'}`);
        }

        const results = await response.json();
        displayResults(results);

    } catch (error) {
        console.error('Erro ao analisar turno:', error);
        resultsOutputDiv.innerHTML = `<p style="color: red;">Falha ao buscar análise: ${error.message}</p>`;
    }
});

function displayResults(results) {
    const resultsOutputDiv = document.getElementById('analysisResultsOutput');
    resultsOutputDiv.innerHTML = ''; // Clear previous

    if (!results || results.length === 0) {
        resultsOutputDiv.innerHTML = '<p>Nenhum resultado de análise retornado ou nenhuma jogada possível.</p>';
        return;
    }

    const ul = document.createElement('ul');
    results.forEach((result, index) => {
        const li = document.createElement('li');
        const probPercent = (result.prob * 100).toFixed(2);
        // outcome is [L0_power, L1_power, L2_power]
        const outcomeStr = `L0: ${result.outcome[0]}, L1: ${result.outcome[1]}, L2: ${result.outcome[2]}`;
        li.textContent = `${index + 1}. Prob: ${probPercent}% | Resultado: (${outcomeStr}) | Ação Sugerida: ${result.action}`;
        ul.appendChild(li);
    });
    resultsOutputDiv.appendChild(ul);
}

// Initial render of empty zones
document.addEventListener('DOMContentLoaded', () => {
    renderZone('hand');
    renderZone('location1');
    renderZone('location2');
    renderZone('location3');
    renderZone('discard');
});
