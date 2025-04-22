function runRsync() {
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;
    const options = document.getElementById('rsyncOptions').value;
    const logOutput = document.getElementById('logOutput').checked;

    const outputArea = document.getElementById('rsyncOutput');
    outputArea.textContent = "[Starting rsync...]\n";

    const eventSource = new EventSourcePolyfill("/run-rsync", {
        headers: {
            "Content-Type": "application/json"
        },
        payload: JSON.stringify({ source, destination, options, log_output: logOutput }),
        method: "POST"
    });

    eventSource.onmessage = function(event) {
        outputArea.textContent += event.data + "\n";
        outputArea.scrollTop = outputArea.scrollHeight;

        if (event.data.includes("Rsync process finished")) {
            loadHistory();
            const confirmMsg = document.createElement('div');
            confirmMsg.style.marginTop = "10px";
            confirmMsg.style.padding = "8px";
            confirmMsg.style.backgroundColor = "#d4edda";
            confirmMsg.style.color = "#155724";
            confirmMsg.style.border = "1px solid #c3e6cb";
            confirmMsg.style.borderRadius = "4px";
            confirmMsg.textContent = "✅ Sync Completed and History Updated";
            document.body.insertBefore(confirmMsg, document.body.firstChild);
            loadHistory();  // Refresh history table without reloading page
        }
    };

    eventSource.onerror = function(err) {
        outputArea.textContent += "[Rsync error or stream ended]\n";
        eventSource.close();
    };
}

// Polyfill EventSource for POST (SSE over POST)
class EventSourcePolyfill {
    constructor(url, options) {
        this.es = null;
        this.init(url, options);
    }

    init(url, options) {
        fetch(url, {
            method: options.method || "POST",
            headers: options.headers,
            body: options.payload
        }).then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            const stream = new ReadableStream({
                start: (controller) => {
                    const read = () => {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                controller.close();
                                return;
                            }
                            const chunk = decoder.decode(value);
                            const lines = chunk.split("\n\n").filter(Boolean);
                            for (let line of lines) {
                                if (this.onmessage) this.onmessage({ data: line.replace(/^data: /, "") });
                            }
                            read();
                        });
                    };
                    read();
                }
            });
            return new Response(stream);
        }).catch(error => {
            if (this.onerror) this.onerror(error);
        });
    }

    close() {
        if (this.es) this.es.close();
    }
}
