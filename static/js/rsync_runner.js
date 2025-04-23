
function runSync() {
  const source = document.getElementById("source-folder").value;
  const destination = document.getElementById("destination-folder").value;
  const options = document.getElementById("rsync-options").value || "-avh --progress";
  const logOutput = document.getElementById("logOutput").checked;

  const statusDiv = document.getElementById("status-message");
  statusDiv.textContent = "Running rsync...";
  statusDiv.style.display = "block";

  const consoleDiv = document.getElementById("rsync-console");
  consoleDiv.innerHTML = "";

  fetch("/run-rsync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, destination, options, log_output: logOutput })
  }).then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    function readChunk() {
      reader.read().then(({ done, value }) => {
        if (done) {
          const p = document.createElement("div");
          p.textContent = "Rsync job completed.";
          p.style.color = "green";
          consoleDiv.appendChild(p);
          loadHistory(); // refresh history
          return;
        }
        const chunk = decoder.decode(value, { stream: true });
        chunk.split("\n").forEach(line => {
          if (line.startsWith("data:")) {
            const msg = line.replace("data: ", "").trim();
            const lineDiv = document.createElement("div");
            lineDiv.textContent = msg;
            consoleDiv.appendChild(lineDiv);
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
          }
        });
        readChunk();
      });
    }

    readChunk();
  });
}

function loadHistory() {
  fetch("/sync-history")
    .then(res => res.json())
    .then(data => {
      const table = document.getElementById("history-table").querySelector("tbody");
      table.innerHTML = "";
      data.forEach(entry => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${entry.source}</td>
          <td>${entry.destination}</td>
          <td>${entry.options}</td>
          <td>${entry.timestamp}</td>
          <td><button onclick='reRun("${entry.source}", "${entry.destination}", "${entry.options}")'>Replay</button></td>
        `;
        table.appendChild(row);
      });
    });
}

function reRun(source, destination, options) {
  document.getElementById("source-folder").value = source;
  document.getElementById("destination-folder").value = destination;
  document.getElementById("rsync-options").value = options;
  runSync();
}
