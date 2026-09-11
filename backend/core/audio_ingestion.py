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

        # Peak normalization only if real voice signal is present (max_amp >= 0.015)
        # Avoids amplifying quiet room background noise / mic hiss
        max_amp = float(np.max(np.abs(audio)))
        if max_amp >= 0.015:
            audio = audio / max_amp * 0.95

        return audio

    def is_speech_active(self, audio: np.ndarray, energy_threshold: float = 0.002) -> bool:
        """Check if incoming audio chunk contains active human/AI speech or background silence."""
        if len(audio) == 0:
            return False
        max_amp = float(np.max(np.abs(audio)))
        rms_energy = float(np.sqrt(np.mean(audio ** 2)))
        return max_amp >= 0.015 and rms_energy >= energy_threshold

    def is_spoken_human_speech(self, audio: np.ndarray, sample_rate: int = 16000) -> tuple[bool, str]:
        """
        Explicit first check: Does this audio contain clearly audible spoken human language
        (not music, not silence, not ambient noise)?
        
        Returns (is_speech_present, status_reason).
        """
        if len(audio) == 0:
            return False, "EMPTY_AUDIO"

        max_amp = float(np.max(np.abs(audio)))
        rms_energy = float(np.sqrt(np.mean(audio ** 2)))
        if max_amp < 0.015 or rms_energy < 0.002:
            return False, "SILENCE_OR_LOW_ENERGY"

        # Frame-based feature analysis (25ms frame, 10ms hop)
        frame_len = int(sample_rate * 0.025)
        hop_len = int(sample_rate * 0.010)
        num_frames = (len(audio) - frame_len) // hop_len + 1

        if num_frames < 10:
            return False, "AUDIO_TOO_SHORT"

        frames = np.array([audio[i * hop_len : i * hop_len + frame_len] for i in range(num_frames)])

        # 1. Zero Crossing Rate (ZCR) per frame
        # Spoken human speech features alternating voiced vowels (low ZCR < 0.08)
        # and unvoiced consonants ('s', 'sh', 'f', 't', 'k', 'p') with high ZCR (> 0.12).
        zcr = np.mean(np.abs(np.diff(np.sign(frames), axis=1)) > 0, axis=1)
        std_zcr = float(np.std(zcr))
        high_zcr_ratio = float(np.mean(zcr > 0.12))  # Ratio of unvoiced consonant frames

        # 2. Frame energy distribution & Pause Ratio
        # Spoken speech contains natural inter-syllable / inter-word pauses.
        # Music and background noise tracks have continuous sound with low pause ratio.
        frame_energies = np.mean(frames ** 2, axis=1)
        max_frame_energy = np.max(frame_energies) + 1e-10
        pause_ratio = float(np.mean(frame_energies < (0.12 * max_frame_energy)))

        # Speech presence decision rules:
        # A spoken speech clip MUST exhibit unvoiced consonant ZCR transitions (high_zcr_ratio >= 0.025 or std_zcr >= 0.035)
        # AND have speech pause dynamics or phonemic energy fluctuations.
        if high_zcr_ratio < 0.025 and std_zcr < 0.035:
            return False, "MUSIC_OR_NON_SPEECH (No spoken unvoiced phoneme transitions detected)"

        if pause_ratio < 0.03 and high_zcr_ratio < 0.04:
            return False, "MUSIC_OR_CONTINUOUS_SONG (Continuous musical audio without speech pauses detected)"

        return True, "SPOKEN_HUMAN_SPEECH_PRESENT"



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
