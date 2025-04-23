
document.addEventListener("DOMContentLoaded", () => {
  loadSavedPaths();
  loadHistory();
});

function loadSavedPaths() {
  fetch("/load-paths")
    .then(res => res.json())
    .then(data => {
      document.getElementById("source-folder").value = data.source || "";
      document.getElementById("destination-folder").value = data.destination || "";
    });
}

function savePaths() {
  const source = document.getElementById("source-folder").value;
  const destination = document.getElementById("destination-folder").value;
  fetch("/save-paths", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, destination })
  }).then(() => showMessage("Paths saved successfully."));
}

function runSync() {
  const source = document.getElementById("source-folder").value;
  const destination = document.getElementById("destination-folder").value;
  const options = document.getElementById("rsync-options").value;
  const logOutput = document.getElementById("logOutput").checked;

  showMessage("Starting sync...", "info");

  fetch("/run-rsync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, destination, options, logOutput })
  })
    .then(res => res.json())
    .then(result => {
      if (result.code === 0) {
        showMessage("Sync completed successfully.");
        loadHistory(true);
      } else {
        showMessage("Sync failed: " + (result.output || result.error), "error");
      }
    });
}

function loadHistory(highlightLast = false) {
  fetch("/sync-history")
    .then(res => res.json())
    .then(data => {
      const table = document.getElementById("history-table").querySelector("tbody");
      table.innerHTML = "";
      data.slice().reverse().forEach((row, index) => {
        const tr = document.createElement("tr");
        if (highlightLast && index === 0) tr.classList.add("history-row-highlight");

        tr.innerHTML = `
          <td>${row.source}</td>
          <td>${row.destination}</td>
          <td>${row.options}</td>
          <td>${new Date(row.timestamp).toLocaleString()}</td>
          <td><button onclick="reRunSync('${row.source}', '${row.destination}', '${row.options}')">Replay</button></td>
        `;
        table.appendChild(tr);
      });
    });
}

function reRunSync(source, destination, options) {
  document.getElementById("source-folder").value = source;
  document.getElementById("destination-folder").value = destination;
  document.getElementById("rsync-options").value = options;
  runSync();
}

function showMessage(text, type = "success") {
  const banner = document.getElementById("status-message");
  banner.textContent = text;
  banner.style.background = type === "error" ? "#ffebee" : "#e8f5e9";
  banner.style.borderLeft = type === "error" ? "5px solid #c62828" : "5px solid #2e7d32";
  banner.style.display = "block";
}
