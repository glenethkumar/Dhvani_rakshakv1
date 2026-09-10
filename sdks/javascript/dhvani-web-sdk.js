/**
 * Dhvani Rakshak - Official JavaScript / WebRTC Web SDK
 * Real-time browser audio stream monitoring & voice cloning prevention.
 */

export class DhvaniRakshakWebSDK {
  constructor(config = {}) {
    self.apiUrl = config.apiUrl || "http://localhost:8000";
    self.wsUrl = config.wsUrl || "ws://localhost:8000/ws/live-stream";
    self.socket = null;
    self.onRiskAlert = config.onRiskAlert || (() => {});
  }

  connectStream() {
    return new Promise((resolve, reject) => {
      this.socket = new WebSocket(this.wsUrl);

      this.socket.onopen = () => {
        console.log("[Dhvani Rakshak SDK] WebSockets stream connected.");
        resolve(true);
      };

      this.socket.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        this.onRiskAlert(payload);
      };

      this.socket.onerror = (err) => {
        console.error("[Dhvani Rakshak SDK] WebSockets error:", err);
        reject(err);
      };
    });
  }

  sendAudioChunk(arrayBuffer) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(arrayBuffer);
    }
  }

  async analyzeFile(file, options = {}) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", options.language || "en-IN");
    if (options.targetSpeakerId) {
      formData.append("target_speaker_id", options.targetSpeakerId);
    }
    formData.append("caller_metadata_json", JSON.stringify(options.callerMetadata || {}));
    formData.append("transaction_context_json", JSON.stringify(options.transactionContext || {}));

    const response = await fetch(`${this.apiUrl}/api/v1/analyze`, {
      method: "POST",
      body: formData
    });
    return await response.json();
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}
