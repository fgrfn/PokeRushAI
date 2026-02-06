const stateList = document.getElementById("state-list");
const editionSelect = document.getElementById("edition-select");
const mapImage = document.getElementById("map-image");
const mapMeta = document.getElementById("map-meta");
const marker = document.getElementById("player-marker");
const scoreboardBody = document.getElementById("scoreboard-body");

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

function renderState(state) {
  stateList.innerHTML = "";
  Object.entries(state).forEach(([key, value]) => {
    const item = document.createElement("li");
    item.textContent = `${key}: ${value}`;
    stateList.appendChild(item);
  });
}

function renderScoreboard(runs) {
  scoreboardBody.innerHTML = "";
  runs.forEach((run) => {
    const row = document.createElement("tr");
    const splitText = (run.split_times || [])
      .map((split) => `${split.name} (${split.time_seconds}s)`)
      .join(", ");
    row.innerHTML = `
      <td>#${run.run_id}</td>
      <td>${run.total_time_seconds.toFixed(2)}</td>
      <td>${splitText || "-"}</td>
    `;
    scoreboardBody.appendChild(row);
  });
}

function updateMarker(state) {
  const x = Number(state.x || 0);
  const y = Number(state.y || 0);
  marker.style.left = `${x * 4}px`;
  marker.style.top = `${y * 4}px`;
}

async function refresh() {
  const maps = await fetchMaps();
  const edition = editionSelect.value;
  const mapConfig = maps[edition];
  if (mapConfig) {
    mapImage.src = mapConfig.map_url;
    mapMeta.textContent = `Map source: ${mapConfig.map_url}`;
  }

  const stateResponse = await fetchState();
  if (stateResponse.status === "ok") {
    renderState(stateResponse.state);
    updateMarker(stateResponse.state);
  }

  const scoreboardResponse = await fetchScoreboard(edition);
  renderScoreboard(scoreboardResponse.runs || []);
}

editionSelect.addEventListener("change", () => {
  refresh();
});

setInterval(refresh, 2000);
refresh();
