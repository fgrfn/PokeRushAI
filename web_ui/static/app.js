const stateList = document.getElementById("state-list");
const mapImage = document.getElementById("map-image");
const mapMeta = document.getElementById("map-meta");
const marker = document.getElementById("player-marker");
const scoreboardBody = document.getElementById("scoreboard-body");
const emulatorStatus = document.getElementById("emulator-status");
const botStatus = document.getElementById("bot-status");
const partyList = document.getElementById("party-list");
const resourcesList = document.getElementById("resources-list");
const metricsList = document.getElementById("metrics-list");
const qlearningList = document.getElementById("qlearning-list");
const actionsPanel = document.getElementById("actions-panel");

// State management
let currentEdition = "red";
let refreshInterval = null;

// Fetch functions
async function fetchMaps() {
  const response = await fetch("/api/maps");
  return response.json();
}

async function fetchState() {
  const response = await fetch("/api/state");
  return response.json();
}

async function fetchScoreboard(edition) {
  const response = await fetch(`/api/scoreboard?edition=${edition}`);
  return response.json();
}

async function fetchParty() {
  const response = await fetch("/api/party");
  return response.json();
}

async function fetchExtendedInfo() {
  const response = await fetch("/api/extended_info");
  return response.json();
}

async function fetchMetrics() {
  const response = await fetch("/api/metrics");
  return response.json();
}

async function fetchControlStatus() {
  const response = await fetch("/api/control/status");
  return response.json();
}

// Render functions
function renderState(state) {
  stateList.innerHTML = "";
  
  const formatters = {
    "edition": (v) => `Edition: ${v}`,
    "location": (v) => `Location: ${v}`,
    "x": (v) => `X: ${v}`,
    "y": (v) => `Y: ${v}`,
    "map_id": (v) => `Map ID: ${v}`,
    "badges": (v) => `Badges: 🏅 ${v}/8`,
    "play_time_seconds": (v) => {
      const hours = Math.floor(v / 3600);
      const minutes = Math.floor((v % 3600) / 60);
      const seconds = Math.floor(v % 60);
      return `Play Time: ${hours}h ${minutes}m ${seconds}s`;
    }
  };
  
  const order = ["edition", "location", "x", "y", "map_id", "badges", "play_time_seconds"];
  
  order.forEach((key) => {
    if (key in state) {
      const item = document.createElement("li");
      const formatter = formatters[key];
      item.textContent = formatter ? formatter(state[key]) : `${key}: ${state[key]}`;
      stateList.appendChild(item);
    }
  });
}

function renderParty(partyData) {
  if (partyData.status !== "ok" || !partyData.party || partyData.party.length === 0) {
    partyList.innerHTML = '<div class="party-placeholder">No party data...</div>';
    return;
  }
  
  partyList.innerHTML = "";
  partyData.party.forEach((pokemon, index) => {
    const div = document.createElement("div");
    div.className = "party-pokemon";
    div.innerHTML = `
      <strong>#${index + 1}: ${pokemon.name || "???"}</strong><br>
      Lv${pokemon.level || "?"} | HP: ${pokemon.hp || 0}/${pokemon.max_hp || 0}
    `;
    partyList.appendChild(div);
  });
}

function renderExtendedInfo(extendedInfo) {
  const money = extendedInfo.money || 0;
  document.getElementById("money-value").textContent = `¥${money}`;
}

function renderMetrics(metrics) {
  document.getElementById("episode-value").textContent = metrics.episode || 0;
  document.getElementById("steps-value").textContent = metrics.steps || 0;
  document.getElementById("reward-value").textContent = (metrics.total_reward || 0).toFixed(2);
  
  // Render recent actions
  if (metrics.recent_actions && metrics.recent_actions.length > 0) {
    actionsPanel.innerHTML = "";
    metrics.recent_actions.slice(-10).reverse().forEach((action) => {
      const div = document.createElement("div");
      div.className = "action-entry";
      div.textContent = `#${action.step}: ${action.action}`;
      actionsPanel.appendChild(div);
    });
  } else {
    actionsPanel.innerHTML = '<div class="log-placeholder">Waiting for bot activity...</div>';
  }
}

function renderQLearningStats(trainingState) {
  const qlearning = trainingState.q_learning || {};
  document.getElementById("states-explored").textContent = qlearning.states_explored || 0;
  document.getElementById("qtable-size").textContent = qlearning.q_table_size || 0;
  document.getElementById("total-updates").textContent = qlearning.total_updates || 0;
}

function renderScoreboard(runs) {
  scoreboardBody.innerHTML = "";
  if (!runs || runs.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="3">No completed runs yet...</td>`;
    scoreboardBody.appendChild(row);
    return;
  }
  runs.forEach((run) => {
    const row = document.createElement("tr");
    const badges = run.badges || "0";
    row.innerHTML = `
      <td>#${run.run_id}</td>
      <td>${run.total_time_seconds ? run.total_time_seconds.toFixed(2) : "-"}</td>
      <td>🏅 ${badges}</td>
    `;
    scoreboardBody.appendChild(row);
  });
}

function updateMarker(state) {
  const x = Number(state.pixel_x || state.x * 4 || 0);
  const y = Number(state.pixel_y || state.y * 4 || 0);
  marker.style.left = `${x}px`;
  marker.style.top = `${y}px`;
}

function updateStatus(controlStatus) {
  const isRunning = controlStatus && controlStatus.running;
  const trainingState = controlStatus.training_state || {};
  
  emulatorStatus.innerHTML = isRunning
    ? 'Emulator: <span class="status-running">Running</span>' 
    : 'Emulator: <span class="status-stopped">Stopped</span>';
  
  const botActive = trainingState.bot_active || false;
  const botStatusText = trainingState.bot_status || "idle";
  
  botStatus.innerHTML = botActive
    ? `Bot: <span class="status-running">${botStatusText}</span>` 
    : 'Bot: <span class="status-stopped">Not Running</span>';
  
  return trainingState;
}

async function refresh() {
  try {
    // Fetch all data in parallel
    const [controlStatus, maps, stateResponse, scoreboardResponse, partyResponse, extendedInfo, metrics] = await Promise.all([
      fetchControlStatus(),
      fetchMaps(),
      fetchState(),
      fetchScoreboard(currentEdition),
      fetchParty(),
      fetchExtendedInfo(),
      fetchMetrics()
    ]);
    
    // Update status and get training state
    const trainingState = updateStatus(controlStatus);
    
    // Render Q-Learning stats
    renderQLearningStats(trainingState);
    
    // Update map
    const mapConfig = maps[currentEdition];
    if (mapConfig) {
      mapImage.src = mapConfig.map_url;
      mapImage.onerror = function() {
        this.onerror = null;
        this.style.display = "none";
        mapMeta.innerHTML = '<span style="color: #e4002b;">⚠ Map not found</span>';
      };
      mapImage.onload = function() {
        this.style.display = "block";
        mapMeta.textContent = `Map: Kanto Region (${currentEdition})`;
      };
    }

    // Update state
    if (stateResponse.status === "ok" || stateResponse.state) {
      const state = stateResponse.state || stateResponse;
      renderState(state);
      updateMarker(state);
      
      if (state.edition) {
        currentEdition = state.edition;
      }
    }

    // Update other panels
    renderParty(partyResponse);
    renderExtendedInfo(extendedInfo);
    renderMetrics(metrics);
    renderScoreboard(scoreboardResponse.runs || scoreboardResponse || []);
    
  } catch (error) {
    console.error("Refresh error:", error);
  }
}

// Auto-refresh every second
refreshInterval = setInterval(refresh, 1000);
refresh();
