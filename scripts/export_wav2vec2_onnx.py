"""
Dhvani Rakshak - Export HuggingFace Wav2Vec2 Model to ONNX Format
Downloads Hemg/wav2vec2-large-xlsr-53-deepfake and converts it to ONNX for real-time streaming.

Usage:
    pip install torch transformers optimum[onnxruntime]
    python scripts/export_wav2vec2_onnx.py
"""

import os
import numpy as np

def export_model(model_id: str = "Hemg/wav2vec2-large-xlsr-53-deepfake", output_path: str = "backend/models/wav2vec2_deepfake.onnx"):
    try:
        import torch
        from transformers import AutoModelForAudioClassification
    except ImportError:
        print("[Export] Error: Please install PyTorch & Transformers: pip install torch transformers")
        return

    print(f"--> Downloading model '{model_id}' from Hugging Face...")
    model = AutoModelForAudioClassification.from_pretrained(model_id)
    model.eval()

    # Create dummy raw 16kHz audio input (1 second = 16000 samples)
    dummy_input = torch.randn(1, 16000, dtype=torch.float32)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"--> Exporting to ONNX format at '{output_path}'...")

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input_values'],
        output_names=['logits'],
        dynamic_axes={
            'input_values': {0: 'batch_size', 1: 'sequence_length'},
            'logits': {0: 'batch_size'}
        }
    )

    print(f" SUCCESS! Model exported to {output_path}")
    print(f"Now you can load '{output_path}' directly with ONNX Runtime in Dhvani Rakshak!")

if __name__ == "__main__":
    export_model()
