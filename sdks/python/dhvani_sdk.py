"""
Dhvani Rakshak - Official Python Client SDK
Enables enterprise applications, banking core gateways, and telecom servers to analyze audio streams.
"""

import requests
import json

class DhvaniRakshakClient:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip("/")

    def health_check(self) -> dict:
        r = requests.get(f"{self.api_url}/api/v1/health")
        return r.json()

    def analyze_audio(
        self,
        audio_filepath: str,
        language: str = "en-IN",
        target_speaker_id: str = None,
        caller_metadata: dict = None,
        transaction_context: dict = None
    ) -> dict:
        """Analyze an audio file against AI voice cloning and impersonation risks."""
        url = f"{self.api_url}/api/v1/analyze"

        metadata_json = json.dumps(caller_metadata or {})
        trans_json = json.dumps(transaction_context or {})

        data = {
            "language": language,
            "caller_metadata_json": metadata_json,
            "transaction_context_json": trans_json
        }
        if target_speaker_id:
            data["target_speaker_id"] = target_speaker_id

        with open(audio_filepath, "rb") as f:
            files = {"file": (audio_filepath, f, "audio/wav")}
            r = requests.post(url, data=data, files=files)
            r.raise_for_status()
            return r.json()

    def enroll_speaker(self, speaker_id: str, audio_filepath: str) -> dict:
        """Enroll a VIP / CXO / family voice sample."""
        url = f"{self.api_url}/api/v1/enroll"
        data = {"speaker_id": speaker_id}
        with open(audio_filepath, "rb") as f:
            files = {"file": (audio_filepath, f, "audio/wav")}
            r = requests.post(url, data=data, files=files)
            r.raise_for_status()
            return r.json()
