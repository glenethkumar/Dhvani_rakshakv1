"""
Dhvani Rakshak - Wav2Vec2 XLSR-53 Deepfake Model Loader
Uses local Hugging Face PyTorch model `Hemgg/Deepfake-audio-detection` for deepfake voice detection.
"""

import os
import numpy as np

class Wav2Vec2DeepFakePyTorch:
    """
    Hugging Face PyTorch Audio Classification Engine using Wav2Vec2 / XLSR-53 architecture.
    Model: Hemgg/Deepfake-audio-detection
    """
    def __init__(self, model_id: str = "Hemgg/Deepfake-audio-detection"):
        self.model_id = model_id
        self.processor = None
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            import torch
            from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

            hf_token = os.getenv("HF_TOKEN")
            kwargs = {"token": hf_token} if hf_token else {}
            print(f"[Wav2Vec2 PyTorch] Loading {self.model_id} from Hugging Face (Authenticated: {bool(hf_token)})...")
            
            self.processor = AutoFeatureExtractor.from_pretrained(self.model_id, **kwargs)
            self.model = AutoModelForAudioClassification.from_pretrained(self.model_id, **kwargs)
            self.model.eval()
            print(f"[Wav2Vec2 PyTorch] Model successfully loaded!")
        except ImportError:
            print("[Wav2Vec2 PyTorch] Error: `torch` or `transformers` not installed. Run: pip install torch transformers")
        except Exception as e:
            print(f"[Wav2Vec2 PyTorch] Failed to load model: {e}")

    def predict(self, audio_16k: np.ndarray) -> dict:
        """Run deepfake inference on raw 16kHz audio numpy array."""
        if self.model is None or self.processor is None:
            return {"error": "Model not loaded. Install torch and transformers."}

        import torch

        # Ensure 1D audio array
        audio_16k = np.squeeze(audio_16k).astype(np.float32)

        # Process raw waveform through feature extractor
        inputs = self.processor(audio_16k, sampling_rate=16000, return_tensors="pt")

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze().cpu().numpy()

        # Dynamically map labels from model config (e.g. {0: 'AIVoice', 1: 'HumanVoice'})
        fake_idx = 1
        real_idx = 0
        if hasattr(self.model.config, "id2label") and self.model.config.id2label:
            for idx, lbl in self.model.config.id2label.items():
                lbl_lower = str(lbl).lower()
                if "ai" in lbl_lower or "fake" in lbl_lower or "spoof" in lbl_lower or "deepfake" in lbl_lower or "generated" in lbl_lower:
                    fake_idx = int(idx)
                elif "human" in lbl_lower or "real" in lbl_lower or "bona" in lbl_lower or "authentic" in lbl_lower:
                    real_idx = int(idx)

        fake_prob = float(probs[fake_idx]) if len(probs) > fake_idx else float(1.0 - probs[real_idx])
        real_prob = float(probs[real_idx]) if len(probs) > real_idx else float(1.0 - fake_prob)

        return {
            "is_deepfake": bool(fake_prob > 0.50),
            "deepfake_probability": round(fake_prob, 4),
            "bona_fide_probability": round(real_prob, 4),
            "model_id": self.model_id,
            "engine": "Hugging Face Wav2Vec2 PyTorch"
        }


# Method 2: Lightweight ONNX Runtime Inference
class Wav2Vec2DeepFakeONNX:
    def __init__(self, onnx_path: str = "backend/models/wav2vec2_deepfake.onnx"):
        self.onnx_path = onnx_path
        self.session = None
        self._load_onnx()

    def _load_onnx(self):
        if not os.path.exists(self.onnx_path):
            print(f"[Wav2Vec2 ONNX] File not found at {self.onnx_path}")
            return

        try:
            import onnxruntime as ort
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self.session = ort.InferenceSession(self.onnx_path, opts)
            print(f"[Wav2Vec2 ONNX] Successfully loaded ONNX model from {self.onnx_path}")
        except Exception as e:
            print(f"[Wav2Vec2 ONNX] Failed to initialize ONNX session: {e}")

    def predict(self, audio_16k: np.ndarray) -> dict:
        """Run fast CPU ONNX inference on raw 16kHz audio numpy array."""
        if self.session is None:
            return {"error": "ONNX model not loaded."}

        audio_16k = np.expand_dims(np.squeeze(audio_16k).astype(np.float32), axis=0)
        input_name = self.session.get_inputs()[0].name

        outputs = self.session.run(None, {input_name: audio_16k})
        logits = outputs[0][0]

        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)

        fake_prob = float(probs[1])
        real_prob = float(probs[0])

        return {
            "is_deepfake": bool(fake_prob > 0.50),
            "deepfake_probability": round(fake_prob, 4),
            "bona_fide_probability": round(real_prob, 4),
            "engine": "ONNX Runtime"
        }

# Aliases for backwards compatibility
Wav2Vec2DeepFakeAPI = Wav2Vec2DeepFakePyTorch
AssemblyAIAudioDetector = Wav2Vec2DeepFakePyTorch
