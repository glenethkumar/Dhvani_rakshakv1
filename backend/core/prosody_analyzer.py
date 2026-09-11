"""
Dhvani Rakshak - Prosody & Behavioral Analyzer
Extracts fundamental frequency (F0) pitch contour via YIN algorithm,
jitter, shimmer, speech rhythm, artificial pause patterns, and emotional flatness.
"""

import numpy as np

class ProsodyAnalyzer:
    def __init__(self, sample_rate: int = 16000, min_f0: float = 60.0, max_f0: float = 400.0):
        self.sample_rate = sample_rate
        self.min_f0 = min_f0
        self.max_f0 = max_f0
        self.min_period = int(sample_rate / max_f0)
        self.max_period = int(sample_rate / min_f0)

    def extract_f0_yin(self, audio: np.ndarray, frame_size: int = 1024, hop_size: int = 512) -> np.ndarray:
        """Extract F0 pitch contour using fast vectorized YIN algorithm."""
        if len(audio) < frame_size:
            audio = np.pad(audio, (0, frame_size - len(audio)))

        num_frames = (len(audio) - frame_size) // hop_size + 1
        f0_contour = np.zeros(num_frames)

        for i in range(num_frames):
            frame = audio[i * hop_size : i * hop_size + frame_size]

            if np.max(np.abs(frame)) < 0.02:
                f0_contour[i] = 0.0
                continue

            # Fast vector difference function using FFT autocorrelation
            w_len = frame_size - self.max_period
            if w_len <= 0:
                continue

            f_base = frame[:w_len]
            # Compute squared difference array for all taus in tau_range
            tau_range = np.arange(self.min_period, self.max_period)
            diff = np.zeros(self.max_period)

            # Vectorized difference across tau
            for tau in range(self.min_period, self.max_period):
                f_shift = frame[tau : tau + w_len]
                diff[tau] = np.sum((f_base - f_shift) ** 2)

            # Cumulative mean normalized difference function (CMNDF)
            cmndf = np.zeros(self.max_period)
            cmndf[0] = 1.0
            cumsum = np.cumsum(diff)
            tau_indices = np.arange(1, self.max_period)
            cmndf[1:] = diff[1:] * tau_indices / (cumsum[1:] + 1e-10)

            # Absolute thresholding
            tau_found = 0
            threshold = 0.20
            valid_taus = np.where((cmndf[self.min_period:self.max_period] < threshold))[0]
            if len(valid_taus) > 0:
                tau_found = self.min_period + valid_taus[0]

            if tau_found > 0:
                pitch = self.sample_rate / tau_found
                f0_contour[i] = pitch if 60.0 <= pitch <= 350.0 else 0.0
            else:
                f0_contour[i] = 0.0  # Unvoiced

        return f0_contour

    def compute_jitter_shimmer(self, audio: np.ndarray, f0_contour: np.ndarray) -> tuple[float, float]:
        """Compute Jitter (pitch perturbation %) and Shimmer (amplitude perturbation in dB)."""
        voiced_f0 = f0_contour[f0_contour > 0]
        if len(voiced_f0) < 3:
            return 0.5, 0.2  # Default baseline for short audio

        periods = 1.0 / voiced_f0
        period_diffs = np.abs(np.diff(periods))
        mean_period = np.mean(periods)
        jitter_pct = float(np.mean(period_diffs) / (mean_period + 1e-10) * 100.0)

        # Shimmer calculation
        frame_size = 512
        num_frames = min(len(f0_contour), len(audio) // frame_size)
        amps = []
        for i in range(num_frames):
            if f0_contour[i] > 0:
                frame_amp = np.max(np.abs(audio[i * frame_size : (i + 1) * frame_size]))
                amps.append(max(1e-5, frame_amp))

        if len(amps) > 2:
            amps = np.array(amps)
            shimmer_db = float(np.mean(np.abs(20 * np.log10(amps[1:] / amps[:-1]))))
        else:
            shimmer_db = 0.3

        return round(jitter_pct, 3), round(shimmer_db, 3)

    def analyze_rhythm_pauses(self, audio: np.ndarray, sample_rate: int = 16000) -> dict:
        """Analyze pause duration regularity and breathing noise presence."""
        frame_len = int(sample_rate * 0.02)  # 20ms frames
        num_frames = len(audio) // frame_len
        if num_frames == 0:
            return {"pause_regularity": 0.5, "unnatural_pauses": False}

        energies = np.array([np.sum(audio[i * frame_len : (i + 1) * frame_len] ** 2) for i in range(num_frames)])
        med_energy = np.median(energies) + 1e-10
        is_silence = energies < (med_energy * 0.1)

        # Count silent run lengths
        silence_runs = []
        curr_run = 0
        for s in is_silence:
            if s:
                curr_run += 1
            else:
                if curr_run > 0:
                    silence_runs.append(curr_run * 20)  # ms
                    curr_run = 0
        if curr_run > 0:
            silence_runs.append(curr_run * 20)

        if len(silence_runs) > 2:
            pause_std = float(np.std(silence_runs))
            # Neural TTS often has artificially uniform pause lengths (e.g. standard deviation < 15ms)
            pause_regularity = float(np.clip(1.0 - pause_std / 120.0, 0.0, 1.0))
        else:
            pause_regularity = 0.2

        return {
            "pause_regularity": round(pause_regularity, 3),
            "unnatural_pauses": pause_regularity > 0.75,
            "silent_pause_count": len(silence_runs)
        }

    def analyze_prosody(self, audio: np.ndarray) -> dict:
        """Perform comprehensive prosody & behavioral analysis."""
        f0_contour = self.extract_f0_yin(audio)
        voiced_f0 = f0_contour[f0_contour > 0]

        if len(voiced_f0) > 0:
            mean_f0 = float(np.mean(voiced_f0))
            std_f0 = float(np.std(voiced_f0))
            min_f0 = float(np.min(voiced_f0))
            max_f0 = float(np.max(voiced_f0))
            f0_range = max_f0 - min_f0
        else:
            mean_f0, std_f0, min_f0, max_f0, f0_range = 150.0, 0.0, 150.0, 150.0, 0.0

        jitter, shimmer = self.compute_jitter_shimmer(audio, f0_contour)
        rhythm_stats = self.analyze_rhythm_pauses(audio)

        # Prosodic Anomaly Score calculation
        # Robotic pitch flatness (std_f0 < 4.0Hz) or zero jitter (< 0.08%) -> Synthetic AI Voice
        # Real human voice naturally has std_f0 >= 5.0Hz and jitter between 0.15% and 12.0%
        if std_f0 < 4.0:
            pitch_flatness_risk = float(np.clip((4.0 - std_f0) / 4.0, 0.0, 1.0))
        else:
            pitch_flatness_risk = 0.0

        jitter_anomaly = float(1.0 if jitter < 0.08 or jitter > 15.0 else 0.0)
        shimmer_anomaly = float(1.0 if shimmer < 0.05 or shimmer > 5.0 else 0.0)

        prosody_anomaly_score = (
            pitch_flatness_risk * 0.45 +
            jitter_anomaly * 0.25 +
            shimmer_anomaly * 0.15 +
            rhythm_stats["pause_regularity"] * 0.15
        )

        return {
            "prosody_anomaly_score": round(float(np.clip(prosody_anomaly_score, 0.02, 0.95)), 4),
            "mean_f0_hz": round(mean_f0, 1),
            "std_f0_hz": round(std_f0, 1),
            "f0_range_hz": round(f0_range, 1),
            "jitter_percent": jitter,
            "shimmer_db": shimmer,
            "rhythm_stats": rhythm_stats
        }

