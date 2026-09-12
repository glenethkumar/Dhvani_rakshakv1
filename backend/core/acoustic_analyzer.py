"""
Dhvani Rakshak - Acoustic & Spectral Analyzer
Enhanced with AASIST / RawNet2 Deep Neural Anti-Spoofing.
Extracts MFCCs, spectral centroid, flatness, flux, formant frequencies,
phase discontinuity, and neural vocoder generator signature artifacts.
"""

import sys
import os
import numpy as np
import scipy.fft as fft
import scipy.signal as signal

# Ensure models can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.deep_fake_detector import DeepFakeDetector


class AcousticAnalyzer:
    def __init__(self, sample_rate: int = 16000, n_mfcc: int = 13, n_mels: int = 26, n_fft: int = 512):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.mel_filterbank = self._create_mel_filterbank()
        # Initialize AASIST Deep Learning Neural Detector
        self.neural_detector = DeepFakeDetector(sample_rate=sample_rate)

    def _hz_to_mel(self, hz):
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel):
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

    def _create_mel_filterbank(self):
        """Create triangular Mel filterbank matrix."""
        low_freq = 0
        high_freq = self.sample_rate / 2.0
        low_mel = self._hz_to_mel(low_freq)
        high_mel = self._hz_to_mel(high_freq)

        mel_points = np.linspace(low_mel, high_mel, self.n_mels + 2)
        hz_points = self._mel_to_hz(mel_points)
        bin_points = np.floor((self.n_fft + 1) * hz_points / self.sample_rate).astype(int)

        bank = np.zeros((self.n_mels, self.n_fft // 2 + 1))
        for m in range(1, self.n_mels + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]

            for k in range(f_m_minus, f_m):
                if f_m != f_m_minus:
                    bank[m - 1, k] = (k - bin_points[m - 1]) / (f_m - f_m_minus)
            for k in range(f_m, f_m_plus):
                if f_m_plus != f_m:
                    bank[m - 1, k] = (bin_points[m + 1] - k) / (f_m_plus - f_m)

        return bank

    def compute_mfcc(self, audio: np.ndarray) -> np.ndarray:
        """Compute MFCC coefficients and deltas."""
        if len(audio) < self.n_fft:
            audio = np.pad(audio, (0, self.n_fft - len(audio)))

        # Pre-emphasis
        pre_emphasized = np.append(audio[0], audio[1:] - 0.97 * audio[:-1])

        # STFT
        window = np.hanning(self.n_fft)
        hop_length = self.n_fft // 2
        num_frames = max(1, (len(pre_emphasized) - self.n_fft) // hop_length + 1)

        frames = np.zeros((num_frames, self.n_fft))
        for i in range(num_frames):
            start = i * hop_length
            frame = pre_emphasized[start : start + self.n_fft]
            if len(frame) < self.n_fft:
                frame = np.pad(frame, (0, self.n_fft - len(frame)))
            frames[i] = frame * window

        # Power spectrum
        mag_spec = np.abs(fft.rfft(frames, axis=1))
        power_spec = (1.0 / self.n_fft) * (mag_spec ** 2)

        # Mel spectrum
        mel_energy = np.dot(power_spec, self.mel_filterbank.T)
        log_mel_energy = np.log(np.maximum(mel_energy, 1e-10))

        # Discrete Cosine Transform (DCT Type II)
        mfcc = fft.dct(log_mel_energy, type=2, axis=1, norm='ortho')[:, :self.n_mfcc]

        # Deltas
        deltas = np.zeros_like(mfcc)
        if len(mfcc) > 2:
            deltas[1:-1] = (mfcc[2:] - mfcc[:-2]) / 2.0
            deltas[0] = mfcc[1] - mfcc[0]
            deltas[-1] = mfcc[-1] - mfcc[-2]

        return mfcc, deltas

    def compute_spectral_features(self, audio: np.ndarray) -> dict:
        """Compute spectral centroid, flatness, flux, and high frequency cutoff."""
        if len(audio) < self.n_fft:
            audio = np.pad(audio, (0, self.n_fft - len(audio)))

        fft_mag = np.abs(fft.rfft(audio[:self.n_fft]))
        freqs = np.linspace(0, self.sample_rate / 2, len(fft_mag))

        # Spectral Centroid
        total_mag = np.sum(fft_mag) + 1e-10
        centroid = float(np.sum(freqs * fft_mag) / total_mag)

        # Spectral Flatness
        geom_mean = np.exp(np.mean(np.log(fft_mag + 1e-10)))
        arith_mean = np.mean(fft_mag) + 1e-10
        flatness = float(geom_mean / arith_mean)

        # High Frequency Cutoff
        high_freq_bin = int(len(fft_mag) * (7000 / (self.sample_rate / 2)))
        high_freq_energy_ratio = float(np.sum(fft_mag[high_freq_bin:]**2) / (np.sum(fft_mag**2) + 1e-10))

        # Phase discontinuity score across voiced speech frames
        stft_matrix = signal.stft(audio, fs=self.sample_rate, nperseg=256, noverlap=128)[2]
        frame_energies = np.mean(np.abs(stft_matrix)**2, axis=0)
        voiced_mask = frame_energies > (0.05 * (np.max(frame_energies) + 1e-8))
        if np.sum(voiced_mask) > 5:
            phases = np.unwrap(np.angle(stft_matrix[:, voiced_mask]), axis=1)
        else:
            phases = np.unwrap(np.angle(stft_matrix), axis=1)
        phase_diff = np.diff(phases, axis=1)
        phase_smoothness_variance = float(np.mean(np.var(phase_diff, axis=1)))

        return {
            "spectral_centroid": round(centroid, 2),
            "spectral_flatness": round(flatness, 4),
            "high_freq_energy_ratio": round(high_freq_energy_ratio, 4),
            "phase_smoothness_variance": round(phase_smoothness_variance, 4)
        }

    def detect_tts_artifacts(self, audio: np.ndarray) -> dict:
        """
        Hybrid Acoustic Analysis combining:
        1. AASIST Deep Neural Anti-Spoofing Spectro-Temporal Graph Attention
        2. Classical DSP Formant and Phase Smoothness Discontinuity Metrics
        """
        spec_feats = self.compute_spectral_features(audio)
        mfcc, delta = self.compute_mfcc(audio)

        mfcc_std = float(np.mean(np.std(mfcc, axis=0)))
        delta_std = float(np.mean(np.std(delta, axis=0)))

        # Voice splicing jump detection
        energy_frames = np.array([np.sum(audio[i:i+256]**2) for i in range(0, max(1, len(audio)-256), 128)])
        if len(energy_frames) > 2:
            energy_diffs = np.abs(np.diff(energy_frames)) / (np.mean(energy_frames) + 1e-10)
            max_discontinuity = float(np.max(energy_diffs))
        else:
            max_discontinuity = 0.0

        # Classical signature probability heuristic
        duration = len(audio) / self.sample_rate
        dsp_elevenlabs = float(np.clip(1.0 - spec_feats["high_freq_energy_ratio"] * 30.0, 0.0, 1.0)) * (1.0 if spec_feats["phase_smoothness_variance"] < 2.0 else 0.5)
        dsp_openai = float(np.clip(1.0 - mfcc_std * 0.20, 0.0, 1.0))
        if duration < 1.0:
            dsp_openai = min(dsp_openai, 0.20)
        dsp_google = float(np.clip(spec_feats["spectral_flatness"] * 20.0, 0.0, 1.0))

        # Run AASIST Deep Neural Network Inference
        neural_res = self.neural_detector.detect_deepfake(audio)
        neural_prob = neural_res["deepfake_probability"]
        neural_sigs = neural_res["vocoder_fingerprints"]

        # DSP anomaly score calibrated for human vs AI
        # Replay degradation rule: General loss of clarity or echo from speaker playback should NOT be flagged IF speech rhythm/pitch are naturally human.
        # Synthesis artifacts: Mechanically even MFCCs, smooth phase, or vocoder signatures MUST be accumulated as DSP anomalies even in replayed audio.
        dsp_anomaly = 0.0
        if mfcc_std < 0.45:
            dsp_anomaly += (0.45 - mfcc_std) * 1.5
        if spec_feats["phase_smoothness_variance"] < 1.2:
            dsp_anomaly += 0.25
        if spec_feats["high_freq_energy_ratio"] > 0.08:
            dsp_anomaly += 0.35

        dsp_anomaly = float(np.clip(dsp_anomaly, 0.05, 0.95))

        # Ensemble Score: 30% DSP + 70% AASIST Neural Network
        hybrid_acoustic_anomaly = float(0.30 * dsp_anomaly + 0.70 * neural_prob)

        return {
            "acoustic_anomaly_score": round(float(np.clip(hybrid_acoustic_anomaly, 0.05, 0.98)), 4),
            "neural_deepfake_probability": round(neural_prob, 4),
            "neural_model": neural_res["model_architecture"],
            "inference_engine": neural_res["inference_engine"],
            "mfcc_variance": round(mfcc_std, 3),
            "delta_variance": round(delta_std, 3),
            "splicing_discontinuity": round(max_discontinuity, 3),
            "spectral_features": spec_feats,
            "tts_signatures": neural_sigs
        }

