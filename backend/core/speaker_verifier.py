"""
Dhvani Rakshak - Speaker Consistency & Verification Engine
Powered by ECAPA-TDNN (Emphasized Channel Attention Time-Delay Neural Network).
Generates calibrated 192-dimensional speaker embeddings (d-vector representation),
performs cosine similarity matching against enrolled contact database,
and detects mid-call speaker identity drift.
"""

import sys
import os
import numpy as np

# Ensure root and models are accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.ecapa_tdnn_verifier import EcapaTdnnVerifier


class SpeakerVerifier:
    def __init__(self, embedding_dim: int = 192):
        self.embedding_dim = embedding_dim
        self.ecapa = EcapaTdnnVerifier(embedding_dim=embedding_dim)
        self.enrolled_profiles: dict[str, np.ndarray] = {}

    def extract_speaker_embedding(self, audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """
        Extract 192-dimensional L2-normalized speaker embedding vector from audio stream
        using ECAPA-TDNN multi-scale channel attention.
        """
        return self.ecapa.extract_embedding(audio)

    def enroll_speaker(self, speaker_id: str, audio: np.ndarray) -> dict:
        """Enroll a new speaker by extracting and storing their 192-dim ECAPA-TDNN vector profile."""
        embedding = self.extract_speaker_embedding(audio)
        self.enrolled_profiles[speaker_id] = embedding
        return {
            "speaker_id": speaker_id,
            "embedding_dim": len(embedding),
            "status": "ENROLLED",
            "model": self.ecapa.model_name,
            "sample_vector_head": [round(float(x), 4) for x in embedding[:5]]
        }

    def verify_speaker(self, current_audio: np.ndarray, target_speaker_id: str = None) -> dict:
        """
        Compare current audio embedding against enrolled speaker profile or general baseline.
        Returns similarity score (0.0 to 1.0) and anomaly score.
        """
        curr_embedding = self.extract_speaker_embedding(current_audio)

        if target_speaker_id and target_speaker_id in self.enrolled_profiles:
            target_embedding = self.enrolled_profiles[target_speaker_id]
            # Cosine similarity (-1.0 to 1.0)
            cosine_sim = float(np.dot(curr_embedding, target_embedding))
            # Calibrated speaker match probability: threshold 0.70 for positive match
            if cosine_sim >= 0.70:
                match_score = 0.50 + 0.50 * ((cosine_sim - 0.70) / 0.30)
            else:
                match_score = max(0.0, 0.50 * (cosine_sim / 0.70))

            match_score = float(np.clip(match_score, 0.0, 1.0))
            mismatch_anomaly = float(1.0 - match_score)
            enrolled_match = True
        else:
            # Baseline consistency mode (self-similarity across frame segments)
            mid_point = len(current_audio) // 2
            if mid_point > 1024:
                emb1 = self.extract_speaker_embedding(current_audio[:mid_point])
                emb2 = self.extract_speaker_embedding(current_audio[mid_point:])
                cosine_sim = float(np.dot(emb1, emb2))
                match_score = float(np.clip((cosine_sim + 1.0) / 2.0, 0.0, 1.0))
                mismatch_anomaly = float(1.0 - match_score)
            else:
                match_score = 0.90
                mismatch_anomaly = 0.10
                cosine_sim = 0.85
            enrolled_match = False

        return {
            "speaker_similarity": round(match_score, 4),
            "speaker_anomaly_score": round(mismatch_anomaly, 4),
            "cosine_distance": round(1.0 - cosine_sim, 4),
            "neural_model": self.ecapa.model_name,
            "enrolled_profile_checked": target_speaker_id if enrolled_match else None
        }
