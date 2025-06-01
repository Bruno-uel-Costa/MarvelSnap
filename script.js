// script.js

const API_BASE_URL = 'http://127.0.0.1:5001'; // Define base URL for API

// --- Data Fundamental (Copied from HTML, assuming it's available or passed) ---
const FULL_DECK_DATA = [
    {'id': 1, 'name': 'Blade', 'cost': 1, 'power': 3, 'is_complex_rng': false, 'is_on_reveal': true, 'ability_text':'On Reveal: Discard the rightmost card from your hand.'},
    {'id': 2, 'name': 'Gambit', 'cost': 3, 'power': 3, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':'On Reveal: Discard a card from your hand to destroy a random enemy card.'},
    {'id': 3, 'name': 'Corvus Glaive', 'cost': 3, 'power': 5, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':'On Reveal: Discard 2 cards from your hand to get +1 Max Energy.'},
    {'id': 4, 'name': 'Jubilee', 'cost': 4, 'power': 1, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':'On Reveal: Add the top card of your deck to this location.'},
    {'id': 5, 'name': 'Ghost Rider', 'cost': 4, 'power': 3, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':'On Reveal: Bring back one of your discarded cards to this location.'},
    {'id': 6, 'name': 'Blink', 'cost': 5, 'power': 7, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':'On Reveal: Swap the last card you played with a card that costs more from your deck.'},
    {'id': 7, 'name': 'Legion', 'cost': 5, 'power': 7, 'is_complex_rng': false, 'is_on_reveal': true, 'ability_text':'On Reveal: Replace each other location with this one.'},
    {'id': 8, 'name': 'Infinity Ultron', 'cost': 5, 'power': 8, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':"On Reveal: Add 2 of Ultron’s Stones to your hand."},
    {'id': 9, 'name': 'Gorr', 'cost': 6, 'power': -1, 'is_complex_rng': false, 'is_on_reveal': false, 'ability_text':'Ongoing: +2 Power for EACH On Reveal card in play.'},
    {'id': 10, 'name': 'Hela', 'cost': 6, 'power': 6, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':'On Reveal: For each different Cost among them, resurrect a card you discarded to a random location.'},
    {'id': 11, 'name': 'Odin', 'cost': 6, 'power': 8, 'is_complex_rng': true, 'is_on_reveal': true, 'ability_text':'On Reveal: Repeat the On Reveal abilities of your other cards here.'},
    {'id': 12, 'name': 'The Infinaut', 'cost': 6, 'power': 20, 'is_complex_rng': false, 'is_on_reveal': false, 'ability_text':'If you played a card last turn, you can’t play this.'},
];

const ULTRON_STONES_DATA = [
    { id: 101, name: 'Mind Stone', cost: 1, power: 1, 'ability_text': 'Stone: Draws a card.' },
    { id: 102, name: 'Power Stone', cost: 1, power: 3, 'ability_text': 'Stone: +1 Power to other cards here.' },
    { id: 103, name: 'Reality Stone', cost: 1, power: 1, 'ability_text': 'Stone: Transforms this location.' },
    { id: 104, name: 'Soul Stone', cost: 1, power: 1, 'ability_text': 'Stone: Afflicts enemy cards here with -1 Power.' },
    { id: 105, name: 'Space Stone', cost: 1, power: 1, 'ability_text': 'Stone: Next turn you can move a card to this location.' },
    { id: 106, name: 'Time Stone', cost: 1, power: 1, 'ability_text': 'Stone: Next turn you get +1 Energy.' }
];

const cardManifest = FULL_DECK_DATA.concat(ULTRON_STONES_DATA).reduce((acc, card) => {
    acc[card.id] = card; // Ensure all relevant card attributes are here for UI logic
    return acc;
}, {});

// --- Estado Global do Jogo (Frontend) ---
let currentGameState = null;
let selectedCardForPlay = null;
let currentTurnActions = [];
let resolvedRandomOutcomesForTurn = [];

// --- DOM Elements ---
let startGameButton, gameBoardDiv, handCardListDiv, locationDivs = [], discardCardListDiv;
let analysisResultsOutputDiv, currentTurnDisplay, currentEnergyDisplay, maxEnergyDisplay, deckSizeDisplay;
let executeTurnButton, endTurnButton, currentTurnActionsListUL, loadingIndicator;
let userInputModal, modalTitle, modalPrompt, modalInputsContainer, modalSubmitButton, modalCancelButton; // Added modalCancelButton

function initializeDOMElements() {
    startGameButton = document.getElementById('startGameButton');
    gameBoardDiv = document.getElementById('gameBoard');
    handCardListDiv = document.getElementById('handCardList');
    locationDivs = [
        document.getElementById('location0CardList'),
        document.getElementById('location1CardList'),
        document.getElementById('location2CardList')
    ];
    discardCardListDiv = document.getElementById('discardCardList');
    analysisResultsOutputDiv = document.getElementById('analysisResultsOutput');
    currentTurnDisplay = document.getElementById('currentTurnDisplay');
    currentEnergyDisplay = document.getElementById('currentEnergyDisplay');
    maxEnergyDisplay = document.getElementById('maxEnergyDisplay');
    deckSizeDisplay = document.getElementById('deckSizeDisplay');
    executeTurnButton = document.getElementById('executeTurnButton');
    endTurnButton = document.getElementById('endTurnButton');
    currentTurnActionsListUL = document.getElementById('currentTurnActionsList');
    loadingIndicator = document.getElementById('loadingIndicator');
    userInputModal = document.getElementById('userInputModal');
    modalTitle = document.getElementById('modalTitle');
    modalPrompt = document.getElementById('modalPrompt');
    modalInputsContainer = document.getElementById('modalInputsContainer');
    modalSubmitButton = document.getElementById('modalSubmitButton');
    modalCancelButton = document.getElementById('modalCancelButton'); // Initialize cancel button
}


// --- Funções de Renderização ---
function renderGameState() {
    if (!currentGameState || !gameBoardDiv) {
        if(gameBoardDiv) gameBoardDiv.style.display = 'none';
        return;
    }
    gameBoardDiv.style.display = 'block';
    currentTurnDisplay.textContent = currentGameState.turn;
    currentEnergyDisplay.textContent = currentGameState.current_energy;
    maxEnergyDisplay.textContent = currentGameState.max_energy;
    deckSizeDisplay.textContent = currentGameState.deck_ids ? currentGameState.deck_ids.length : currentGameState.deck_size;

    renderZoneCards(handCardListDiv, currentGameState.hand_ids || [], 'hand');
    for(let i = 0; i < 3; i++) {
        if (locationDivs[i]) renderZoneCards(locationDivs[i], currentGameState.locations[i] || [], 'location', i);
        if (document.getElementById(`location${i}Count`)) document.getElementById(`location${i}Count`).textContent = (currentGameState.locations[i] || []).length;
    }
    renderZoneCards(discardCardListDiv, currentGameState.discard_ids || [], 'discard');

    if (document.getElementById('handCount')) document.getElementById('handCount').textContent = (currentGameState.hand_ids || []).length;
    if (document.getElementById('discardCount')) document.getElementById('discardCount').textContent = (currentGameState.discard_ids || []).length;

    renderCurrentTurnActions();
}

function renderZoneCards(zoneDiv, cardIds, zoneType, locationIndex = -1) {
    if (!zoneDiv) return;
    zoneDiv.innerHTML = '';
    (cardIds || []).forEach(id => {
        const cardData = cardManifest[id] || { name: `ID ${id}`, cost: '?', power: '?' };
        const cardDiv = document.createElement('div');
        cardDiv.classList.add('card-item');
        cardDiv.textContent = `${cardData.name} (C:${cardData.cost} P:${cardData.power})`;
        if (zoneType === 'hand') {
            cardDiv.onclick = () => selectCardForPlay(cardData);
        }
        zoneDiv.appendChild(cardDiv);
    });
}

function renderCurrentTurnActions() {
    if (!currentTurnActionsListUL) return;
    currentTurnActionsListUL.innerHTML = '';
    currentTurnActions.forEach((action, index) => {
        const cardData = cardManifest[action.card_id];
        const li = document.createElement('li');
        li.textContent = `Jogar ${cardData.name} no Local ${action.location_index + 1}`;
        const removeActionBtn = document.createElement('button');
        removeActionBtn.textContent = 'X';
        removeActionBtn.onclick = () => {
            currentTurnActions.splice(index, 1);
            resolvedRandomOutcomesForTurn = resolvedRandomOutcomesForTurn.filter(r => r.action_index !== index).map(r => {
                if (r.action_index > index) r.action_index--; // Adjust indices
                return r;
            });
            renderCurrentTurnActions();
        };
        li.appendChild(removeActionBtn);
        currentTurnActionsListUL.appendChild(li);
    });
}

// --- Lógica de Interação ---
function selectCardForPlay(cardData) {
    if (!currentGameState || cardData.cost > currentGameState.current_energy - calculateStagedEnergyCost()) {
        alert(`Energia insuficiente para selecionar ${cardData.name}.`);
        return;
    }
    selectedCardForPlay = cardData;
    alert(`${selectedCardForPlay.name} selecionado. Clique em um local para adicioná-lo à fila de ações.`);
    highlightValidLocationTargets(true);
}

function calculateStagedEnergyCost() {
    return currentTurnActions.reduce((sum, action) => sum + (cardManifest[action.card_id]?.cost || 0), 0);
}

function highlightValidLocationTargets(enable) {
    locationDivs.forEach((locDiv, index) => {
        if (!locDiv || !currentGameState) return;
        if (enable && selectedCardForPlay && (currentGameState.locations[index] || []).length < 4) {
            locDiv.classList.add('valid-target');
            locDiv.onclick = () => attemptPlayToLocation(index); // Add click listener
        } else {
            locDiv.classList.remove('valid-target');
            locDiv.onclick = null; // Remove click listener
        }
    });
}

window.attemptPlayToLocation = async function(locationIndex) {
    if (!selectedCardForPlay || !currentGameState) return;
    if ((currentGameState.locations[locationIndex] || []).length >= 4) {
        alert(`Local ${locationIndex + 1} está cheio.`);
        return;
    }
    const action = { type: "PLAY_CARD", card_id: selectedCardForPlay.id, location_index: locationIndex };
    const rngOutcome = await promptForRNG(selectedCardForPlay);

    if (rngOutcome === 'cancel') {
        selectedCardForPlay = null;
        highlightValidLocationTargets(false);
        return;
    }
    if(rngOutcome) {
         resolvedRandomOutcomesForTurn.push({ ...rngOutcome, action_index: currentTurnActions.length });
    }
    currentTurnActions.push(action);
    renderCurrentTurnActions();
    selectedCardForPlay = null;
    highlightValidLocationTargets(false);
}

async function promptForRNG(cardData) {
    return new Promise(resolve => {
        if (!userInputModal || !modalTitle || !modalPrompt || !modalInputsContainer || !modalSubmitButton || !modalCancelButton) {
            console.error("Modal elements not found!");
            resolve(null);
            return;
        }

        const card_id_for_rng = cardData.id;
        let requiresInput = false;

        if (cardData.name === "Corvus Glaive") {
            requiresInput = true;
            modalTitle.textContent = `Corvus Glaive - Escolha os Descartados`;
            modalPrompt.textContent = "Quais 2 cartas Corvus Glaive descartou da sua mão?";
            modalInputsContainer.innerHTML = `
                <label>Carta 1 Descartada:</label> <select id="corvusDiscard1" class="mb-2">${populateHandOptions(card_id_for_rng)}</select>
                <label>Carta 2 Descartada:</label> <select id="corvusDiscard2">${populateHandOptions(card_id_for_rng)}</select>
            `;
            modalSubmitButton.onclick = () => {
                const discard1 = document.getElementById('corvusDiscard1').value;
                const discard2 = document.getElementById('corvusDiscard2').value;
                if (discard1 && discard2 && discard1 !== discard2) {
                    userInputModal.style.display = 'none';
                    resolveModalPromise({ source_card_id: card_id_for_rng, outcome_type: "CORVUS_DISCARD", discarded_ids: [parseInt(discard1), parseInt(discard2)] });
                } else if (discard1 === "" && discard2 === "") { // Allow specifying no discards if hand is small
                     userInputModal.style.display = 'none';
                     resolveModalPromise({ source_card_id: card_id_for_rng, outcome_type: "CORVUS_DISCARD", discarded_ids: [] });
                } else if (discard1 && discard2 === "") { // Allow specifying one discard
                     userInputModal.style.display = 'none';
                     resolveModalPromise({ source_card_id: card_id_for_rng, outcome_type: "CORVUS_DISCARD", discarded_ids: [parseInt(discard1)] });
                }
                 else {
                    alert("Por favor, selecione cartas válidas (diferentes ou nenhuma/uma se apropriado).");
                }
            };
        } else if (cardData.name === "Infinity Ultron") {
            requiresInput = true;
            modalTitle.textContent = `Infinity Ultron - Pedras Geradas`;
            modalPrompt.textContent = "Quais 2 Pedras do Infinito o Ultron gerou?";
            modalInputsContainer.innerHTML = `
                <label>Pedra 1:</label> <select id="ultronStone1" class="mb-2">${populateStoneOptions()}</select>
                <label>Pedra 2:</label> <select id="ultronStone2">${populateStoneOptions()}</select>
            `;
            modalSubmitButton.onclick = () => {
                const stone1 = document.getElementById('ultronStone1').value;
                const stone2 = document.getElementById('ultronStone2').value;
                 if (stone1 && stone2 && stone1 !== stone2) {
                    userInputModal.style.display = 'none';
                    resolveModalPromise({ source_card_id: card_id_for_rng, outcome_type: "ULTRON_STONES", generated_stone_ids: [parseInt(stone1), parseInt(stone2)] });
                } else {
                    alert("Por favor, selecione duas pedras diferentes.");
                }
            };
        } else if (cardData.name === "Jubilee" || cardData.name === "Ghost Rider") {
             requiresInput = true;
             const sourceZoneIds = cardData.name === "Jubilee" ? currentGameState.deck_ids : currentGameState.discard_ids;
             const promptText = cardData.name === "Jubilee" ?
                (sourceZoneIds && sourceZoneIds.length > 0 ? "Qual carta a Jubilee puxou do baralho?" : "Baralho vazio, nenhuma carta para Jubilee puxar.") :
                (sourceZoneIds && sourceZoneIds.length > 0 ? "Qual carta o Ghost Rider ressuscitou do descarte?" : "Pilha de descarte vazia, nenhuma carta para Ghost Rider.");

             modalTitle.textContent = `${cardData.name} - Resultado do Efeito`;
             modalPrompt.textContent = promptText;
             if (sourceZoneIds && sourceZoneIds.length > 0) {
                modalInputsContainer.innerHTML = `<label>Carta Resultante:</label> <select id="effectCard">${populateSpecificCardOptions(sourceZoneIds)}</select>`;
             } else {
                modalInputsContainer.innerHTML = `<p>Nenhuma carta elegível na zona de origem.</p>`;
             }
             modalSubmitButton.onclick = () => {
                const effectCardId = sourceZoneIds && sourceZoneIds.length > 0 ? document.getElementById('effectCard').value : null;
                if(effectCardId){
                    userInputModal.style.display = 'none';
                    const outcome_type = cardData.name === "Jubilee" ? "JUBILEE_PULL" : "GHOST_RIDER_CHOICE";
                    const key_name = cardData.name === "Jubilee" ? "pulled_card_id" : "resurrected_id";
                    let outcomeData = { source_card_id: card_id_for_rng, outcome_type: outcome_type};
                    outcomeData[key_name] = parseInt(effectCardId);
                    resolveModalPromise(outcomeData);
                } else if (!(sourceZoneIds && sourceZoneIds.length > 0)) { // No cards were available
                    userInputModal.style.display = 'none';
                    resolveModalPromise(null); // No choice to make, no outcome to report
                }
                 else {
                    alert("Por favor, selecione uma carta.");
                }
             };
        }

        if(requiresInput) {
            userInputModal.style.display = 'block';
            resolveModalPromise = value => resolve(value); // Store resolve function
            modalCancelButton.onclick = () => { // Handle cancel
                userInputModal.style.display = 'none';
                resolveModalPromise('cancel'); // Resolve with 'cancel'
            };
        } else {
            resolve(null); // No RNG input needed for this card
        }
    });
}


function populateHandOptions(excludeCardId = null) {
    let options = '<option value="">Nenhuma/Auto</option>'; // Allow "no discard" or auto-resolve
    if (currentGameState && currentGameState.hand_ids) {
        currentGameState.hand_ids.forEach(id => {
            // Allow selecting the card being played if it's a discard cost (though Corvus isn't)
            // For Corvus, he shouldn't be in hand when his ability resolves.
            if (id !== excludeCardId || cardManifest[id]?.name === "Corvus Glaive") {
                 options += `<option value="${id}">${cardManifest[id] ? cardManifest[id].name : 'ID '+id}</option>`;
            }
        });
    }
    return options;
}
function populateStoneOptions() {
    let options = '<option value="">Selecione...</option>';
    ULTRON_STONES_DATA.forEach(stone => {
         options += `<option value="${stone.id}">${stone.name}</option>`;
    });
    return options;
}
function populateSpecificCardOptions(cardIdList) {
     let options = '<option value="">Selecione...</option>';
    if (cardIdList && cardIdList.length > 0) {
        cardIdList.forEach(id => {
             options += `<option value="${id}">${cardManifest[id] ? cardManifest[id].name : 'ID '+id}</option>`;
        });
    } else {
        options = '<option value="">Nenhuma carta disponível</option>';
    }
    return options;
}

// --- Funções de API ---
async function fetchApi(endpoint, method = 'GET', payload = null) {
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    if (analysisResultsOutputDiv && method !== 'GET') analysisResultsOutputDiv.innerHTML = '<p>Analisando...</p>';

    const fullUrl = API_BASE_URL + endpoint;
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (payload && method !== 'GET') {
        options.body = JSON.stringify(payload);
    }

    try {
        const response = await fetch(fullUrl, options);
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({error: "Erro desconhecido ao decodificar JSON de erro do servidor."}));
            throw new Error(errorData.error || `Erro do Servidor: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        console.error(`Erro em ${method} ${fullUrl}:`, error);
        if (analysisResultsOutputDiv) analysisResultsOutputDiv.innerHTML = `<p style="color: red;">Erro na comunicação com o servidor: ${error.message}</p>`;
        return null;
    }
}

function displayAnalysisResults(analysisData) {
    if (!analysisResultsOutputDiv) return;
    analysisResultsOutputDiv.innerHTML = '';

    let outcomesList;
    if (analysisData && Array.isArray(analysisData)) {
        outcomesList = analysisData;
    } else if (analysisData && analysisData.top_10_outcomes && Array.isArray(analysisData.top_10_outcomes)) {
        outcomesList = analysisData.top_10_outcomes;
    } else {
        analysisResultsOutputDiv.innerHTML = '<p>Nenhum resultado provável encontrado ou formato de dados de análise inesperado.</p>';
        return;
    }

    if (outcomesList.length === 0) {
        analysisResultsOutputDiv.innerHTML = '<p>Nenhum resultado provável encontrado ou nenhuma jogada possível.</p>';
        return;
    }

    const ul = document.createElement('ul');
    ul.classList.add('list-disc', 'pl-5', 'space-y-1'); // Adjusted spacing
    outcomesList.forEach((result, index) => {
        const li = document.createElement('li');
        li.classList.add('text-sm', 'p-1'); // Smaller text, some padding
        const probPercent = (result.prob * 100).toFixed(2);
        const outcome = result.outcome;
        const action = result.action;
        li.innerHTML = `
            <span class="font-semibold">Prob: ${probPercent}%</span> |
            Res: <span class="font-mono text-blue-600">(${outcome[0]}, ${outcome[1]}, ${outcome[2]})</span> |
            Ação: <span class="italic text-gray-700">${action}</span>`;
        ul.appendChild(li);
    });
    resultsOutputDiv.appendChild(ul);
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    initializeDOMElements();

    if (startGameButton) {
        startGameButton.addEventListener('click', async () => {
            const gameData = await fetchApi('/api/start_game', 'GET');
            if (gameData) {
                currentGameState = gameData;
                currentTurnActions = [];
                resolvedRandomOutcomesForTurn = [];
                renderGameState();
                const initialAnalysisPayload = { current_game_state: currentGameState };
                const analysisResult = await fetchApi('/api/get_next_turn_analysis', 'POST', initialAnalysisPayload);
                if (analysisResult) displayAnalysisResults(analysisResult);
            }
        });
    }

    if (executeTurnButton) {
        executeTurnButton.addEventListener('click', async () => {
            if (!currentGameState) {
                alert("Inicie um jogo primeiro.");
                return;
            }
            if (currentTurnActions.length === 0) {
                alert("Nenhuma ação para executar neste turno.");
                return;
            }
            const payload = {
                current_game_state: currentGameState,
                player_actions: currentTurnActions,
                resolved_random_outcomes: resolvedRandomOutcomesForTurn
            };
            const result = await fetchApi('/api/execute_actions_and_analyze', 'POST', payload);
            if (result && result.game_state_after_actions && result.next_turn_analysis) {
                currentGameState = result.game_state_after_actions;
                renderGameState();
                displayAnalysisResults(result.next_turn_analysis);
                currentTurnActions = [];
                resolvedRandomOutcomesForTurn = [];
            }
        });
    }

    if (endTurnButton) {
        endTurnButton.addEventListener('click', async () => {
            if (!currentGameState) {
                alert("Inicie um jogo primeiro.");
                return;
            }
            if (currentTurnActions.length > 0) {
                if(!confirm("Você tem ações planejadas que não foram executadas. Deseja finalizar o turno mesmo assim?")){
                    return;
                }
            }
            const payload = { current_game_state_at_turn_end: currentGameState };
            const result = await fetchApi('/api/advance_turn_and_analyze', 'POST', payload);
            if (result && result.new_turn_game_state && result.current_turn_analysis) {
                currentGameState = result.new_turn_game_state;
                currentTurnActions = [];
                resolvedRandomOutcomesForTurn = [];
                renderGameState();
                displayAnalysisResults(result.current_turn_analysis);
            }
        });
    }

    if (userInputModal && modalCancelButton) { // Ensure cancel button exists
        modalCancelButton.onclick = () => {
            userInputModal.style.display = 'none';
            if (resolveModalPromise) resolveModalPromise('cancel'); // Resolve with 'cancel'
        };
    } else {
        console.warn("Modal cancel button not found.");
    }

    if (gameBoardDiv) {
        gameBoardDiv.style.display = 'none';
    } else {
        console.warn("gameBoardDiv not found on DOMContentLoaded. UI might not behave as expected if elements are missing.");
    }
});
