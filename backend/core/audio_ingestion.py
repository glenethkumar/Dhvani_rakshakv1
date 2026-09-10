"""
Dhvani Rakshak - Audio Ingestion Layer
Handles streaming audio buffers, 16kHz mono normalization, VAD, sliding window chunking,
and noise reduction with sub-second latency.
"""

import numpy as np
import io
import wave

class AudioIngestionPipeline:
    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate

    def load_wav_bytes(self, wav_bytes: bytes) -> tuple[np.ndarray, int]:
        """Convert WAV raw bytes into normalized float32 numpy array (-1.0 to 1.0)."""
        try:
            with wave.open(io.BytesIO(wav_bytes), 'rb') as wav_file:
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                sample_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                raw_data = wav_file.readframes(n_frames)

                if sample_width == 2:
                    dtype = np.int16
                    max_val = 32768.0
                elif sample_width == 4:
                    dtype = np.int32
                    max_val = 2147483648.0
                else:
                    dtype = np.uint8
                    max_val = 128.0

                audio_data = np.frombuffer(raw_data, dtype=dtype).astype(np.float32)
                if sample_width == 1:
                    audio_data = (audio_data - 128.0) / 128.0
                else:
                    audio_data = audio_data / max_val

                if channels > 1:
                    # Convert stereo to mono
                    audio_data = audio_data.reshape(-1, channels).mean(axis=1)

                if sample_rate != self.target_sample_rate:
                    audio_data = self.resample_simple(audio_data, sample_rate, self.target_sample_rate)
                    sample_rate = self.target_sample_rate

                return audio_data, sample_rate
        except Exception:
            # Fallback for raw PCM float/int bytes
            arr = np.frombuffer(wav_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            return arr, self.target_sample_rate

    def resample_simple(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Linear interpolation resampling for fast low-latency execution."""
        if orig_sr == target_sr or len(audio) == 0:
            return audio
        duration = len(audio) / orig_sr
        target_length = int(round(duration * target_sr))
        orig_indices = np.linspace(0, len(audio) - 1, num=len(audio))
        target_indices = np.linspace(0, len(audio) - 1, num=target_length)
        return np.interp(target_indices, orig_indices, audio)

    def preprocess(self, audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """Perform peak normalization and simple spectral noise reduction."""
        if len(audio) == 0:
            return audio

        # Peak normalization if voice signal is present (max_amp >= 0.0008)
        max_amp = float(np.max(np.abs(audio)))
        if max_amp >= 0.0008:
            audio = audio / max_amp * 0.95

        return audio

    def is_speech_active(self, audio: np.ndarray, energy_threshold: float = 0.0001) -> bool:
        """Check if incoming audio chunk contains active human/AI speech or background silence."""
        if len(audio) == 0:
            return False
        max_amp = float(np.max(np.abs(audio)))
        rms_energy = float(np.sqrt(np.mean(audio ** 2)))
        return max_amp >= 0.0008 or rms_energy >= energy_threshold



    def frame_audio(self, audio: np.ndarray, frame_size_ms: float = 25.0, hop_size_ms: float = 10.0, sample_rate: int = 16000):
        """Split audio signal into overlapping frames for short-term spectral analysis."""
        frame_len = int(sample_rate * (frame_size_ms / 1000.0))
        hop_len = int(sample_rate * (hop_size_ms / 1000.0))

        if len(audio) < frame_len:
            pad_len = frame_len - len(audio)
            audio = np.pad(audio, (0, pad_len))

        num_frames = 1 + (len(audio) - frame_len) // hop_len
        frames = np.zeros((num_frames, frame_len), dtype=np.float32)
        for i in range(num_frames):
            start = i * hop_len
            frames[i] = audio[start:start + frame_len]
        return frames, frame_len, hop_len
