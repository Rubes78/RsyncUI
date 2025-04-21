function openBrowser(fieldId) {
    const iframe = document.getElementById('browserFrame');
    iframe.src = '/browse?path=/&field=' + encodeURIComponent(fieldId);
}

function updateSummary() {
    const src = document.getElementById('source').value || "[not selected]";
    const dst = document.getElementById('destination').value || "[not selected]";
    document.getElementById('summarySource').innerText = src;
    document.getElementById('summaryDestination').innerText = dst;
}

function savePaths() {
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;

    if (!source || !destination) {
        alert("Please select both source and destination folders before saving.");
        return;
    }

    fetch("/save-paths", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: source, destination: destination })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        } else {
            alert("Error saving paths: " + (data.error || "Unknown error"));
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Error communicating with server.");
    });
}

function clearSelections() {
    document.getElementById('source').value = "";
    document.getElementById('destination').value = "";
    updateSummary();
}

function loadSavedPaths() {
    fetch("/load-paths")
        .then(res => res.json())
        .then(data => {
            console.log("Loaded saved paths:", data);
            if (data.error) {
                console.warn("No saved paths loaded:", data.error);
                return;
            }
            if (data.source) {
                document.getElementById('source').value = data.source;
            }
            if (data.destination) {
                document.getElementById('destination').value = data.destination;
            }
            updateSummary();
        })
        .catch((err) => {
            console.warn("Error loading saved paths:", err);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM loaded, binding events");
    loadSavedPaths();

    document.getElementById('source').addEventListener('input', updateSummary);
    document.getElementById('destination').addEventListener('input', updateSummary);
    document.getElementById('saveButton').addEventListener('click', savePaths);
});
