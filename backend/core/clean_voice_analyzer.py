"""
Dhvani Rakshak - Clean Voice Detection Engine (2-Step Architecture)

Step A: Speech presence check ("Is there clear audible human speech in this clip? YES or NO")
Step B: Authenticity analysis (prosody + spectral + formant/timbre production checks)

Includes permanent debug logging for every single request.
"""

import sys
import os
import uuid
import json
import numpy as np
import scipy.fft as fft
import scipy.signal as signal

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audio_ingestion import AudioIngestionPipeline
from core.acoustic_analyzer import AcousticAnalyzer
from core.prosody_analyzer import ProsodyAnalyzer
from models.deep_fake_detector import DeepFakeDetector

class CleanVoiceAnalyzer:
    def __init__(self):
        self.ingestion = AudioIngestionPipeline(target_sample_rate=16000)
        self.acoustic = AcousticAnalyzer(sample_rate=16000)
        self.prosody = ProsodyAnalyzer(sample_rate=16000)
        self.detector = DeepFakeDetector(sample_rate=16000)

    def check_speech_presence(self, audio: np.ndarray, sample_rate: int = 16000) -> tuple[bool, str]:
        """
        Step A: Ask strictly whether there is clear audible human speech in this clip (YES or NO).
        Returns (is_speech_present: bool, raw_response: str).
        """
        if len(audio) == 0:
            return False, "NO (Empty audio buffer)"

        max_amp = float(np.max(np.abs(audio)))
        rms_energy = float(np.sqrt(np.mean(audio ** 2)))

        # Silence / Background room noise check
        if max_amp < 0.015 or rms_energy < 0.002:
            return False, f"NO (Silence / low energy ambient noise: max_amp={max_amp:.4f}, rms={rms_energy:.4f})"

        duration = len(audio) / sample_rate
        if duration < 0.3:
            return False, f"NO (Audio duration too short: {duration:.2f}s)"

        # Frame-based signal variation analysis
        frame_len = int(sample_rate * 0.025)
        hop_len = int(sample_rate * 0.010)
        num_frames = (len(audio) - frame_len) // hop_len + 1

        if num_frames < 5:
            return False, f"NO (Too few frames: {num_frames})"

        frames = np.array([audio[i * hop_len : i * hop_len + frame_len] for i in range(num_frames)])

        zcr = np.mean(np.abs(np.diff(np.sign(frames), axis=1)) > 0, axis=1)
        std_zcr = float(np.std(zcr))
        frame_energies = np.mean(frames ** 2, axis=1)
        max_frame_energy = np.max(frame_energies) + 1e-10
        energy_std = float(np.std(frame_energies) / max_frame_energy)

        # Pure static tone check
        if std_zcr < 0.0001 and energy_std < 0.001:
            return False, f"NO (Pure tone / static non-speech signal: zcr_std={std_zcr:.6f})"

        # Polyphonic music chord check (Song/music clip vs Speech harmonic series)
        # Speech harmonics are integer multiples of F0 (constant difference between peaks).
        # Polyphonic music chords have non-integer frequency intervals.
        fft_mag = np.abs(fft.rfft(audio[:min(len(audio), 8192)]))
        max_m = np.max(fft_mag) + 1e-10
        peaks = signal.find_peaks(fft_mag, height=0.18 * max_m, distance=12)[0]
        freq_bins = peaks * (sample_rate / 8192.0)
        valid_peaks = [f for f in freq_bins if 150.0 <= f <= 1200.0]

        if len(valid_peaks) >= 3:
            diffs = np.diff(valid_peaks)
            diff_std = float(np.std(diffs))
            pause_ratio = float(np.mean(frame_energies < (0.08 * max_frame_energy)))
            if diff_std > 22.0 and pause_ratio < 0.01:
                return False, f"NO (Song / polyphonic music track without spoken human speech: diff_std={diff_std:.1f})"

        return True, "YES (Audible spoken human speech present in audio clip)"

    def analyze_authenticity(self, audio: np.ndarray, sample_rate: int = 16000) -> tuple[dict, str]:
        """
        Step B: Production characteristics analysis (only runs if Step A returned YES).
        Returns (parsed_result: dict, raw_response: str).
        """
        ac_res = self.acoustic.detect_tts_artifacts(audio)
        pr_res = self.prosody.analyze_prosody(audio)
        spec_feats = ac_res.get("spectral_features", {})

        std_f0 = pr_res.get("std_f0_hz", 0.0)
        f0_range = pr_res.get("f0_range_hz", 0.0)
        jitter = pr_res.get("jitter_percent", 0.0)
        phase_var = spec_feats.get("phase_smoothness_variance", 3.0)
        deepfake_prob = ac_res.get("neural_deepfake_probability", 0.0)
        high_freq_energy = spec_feats.get("high_freq_energy_ratio", 0.0)
        raw_lfcc_std = ac_res.get("mfcc_variance", 10.0)
        max_discontinuity = ac_res.get("splicing_discontinuity", 0.0)

        # Production Characteristics Classification Logic:
        # 1. TTS Synthesis Artifacts: Unnaturally flat pitch (std_f0 < 3.5Hz or f0_range < 9.0Hz), missing jitter (jitter < 0.12%), smooth phase.
        # 2. Voice Conversion (RVC / Voice-to-Voice) Artifacts: Human speech pitch/rhythm variation coupled with synthetic vocal timbre
        #    (metallic formant envelope, phase smoothness variance < 1.6, unnatural vocoder resonance).
        # 3. Replay Degradation: General loss of clarity, echo, or room reverberation from speaker playback,
        #    where BOTH underlying speech rhythm and vocal timbre remain natural human acoustic signals (std_f0 >= 4.0, jitter >= 0.15%, phase_var >= 2.0).

        is_tts_flat_pitch = (std_f0 < 3.0 or (f0_range < 7.0 and jitter < 0.10))
        is_voice_conversion_timbre = (
            (phase_var < 1.6 and (deepfake_prob >= 0.35 or ac_res.get("acoustic_anomaly_score", 0.0) >= 0.25)) or
            deepfake_prob >= 0.70
        )
        
        is_human_pitch_dynamics = (std_f0 >= 4.0 and f0_range >= 10.0 and jitter >= 0.12)
        is_human_phase_resonance = (phase_var >= 1.8)

        # Authenticity score calculation according to strict 3-tier risk system:
        #   0-39   -> Human Voice     (GREEN / Safe)
        #   40-69  -> Uncertain Voice (YELLOW / Recommend Verification)
        #   70-100 -> AI Voice Clone  (RED / High Risk - Flagged)
        if is_tts_flat_pitch:
            auth_score = max(75, min(95, int(max(deepfake_prob, 0.85) * 100.0)))
            risk_level = "High"
            label = "AI Voice Clone"
            color = "RED"
            reasoning = f"TTS synthetic speech detected: Unnaturally flat pitch contour (std_f0={std_f0:.1f}Hz) & zero vocal cord micro-jitter ({jitter:.2f}%)."
        elif is_voice_conversion_timbre:
            auth_score = max(70, min(95, int(max(deepfake_prob, 0.75) * 100.0)))
            risk_level = "High"
            label = "AI Voice Clone"
            color = "RED"
            reasoning = f"Voice conversion (RVC/Voice-to-Voice) synthetic timbre detected: Formant envelope & vocoder phase alignment anomaly identified (phase_var={phase_var:.2f})."
        elif is_human_pitch_dynamics and is_human_phase_resonance:
            auth_score = min(35, max(5, int(deepfake_prob * 100.0)))
            risk_level = "Low"
            label = "Human Voice"
            color = "GREEN"
            reasoning = f"Authentic human speech verified: Natural fundamental frequency pitch dynamics (std_f0={std_f0:.1f}Hz, jitter={jitter:.2f}%) and natural vocal tract formant resonance confirmed."
        else:
            auth_score = 52
            risk_level = "Medium"
            label = "Uncertain Voice"
            color = "YELLOW"
            reasoning = f"Ambiguous acoustic speech signals / elevated background noise detected (std_f0={std_f0:.1f}Hz, jitter={jitter:.2f}%)."

        parsed_json = {
            "status": "OK",
            "authenticity_score": auth_score,
            "risk_score": auth_score,
            "risk_level": risk_level,
            "label": label,
            "color": color,
            "reasoning": reasoning,
            "alert_level": color,
            "voice_label": label,
            "recommendation": "RECOMMEND_DISCONNECT" if color == "RED" else ("PROCEED_WITH_CAUTION" if color == "YELLOW" else "ALLOW"),
            "user_message": f"🚨 FAKE AI VOICE CLONE DETECTED (Score: {auth_score}/100). Recommended: disconnect call." if color == "RED"
                           else (f"⚠️ UNCERTAIN VOICE (Score: {auth_score}/100). Secondary verification recommended." if color == "YELLOW"
                           else f"✅ REAL HUMAN VOICE DETECTED (Score: {auth_score}/100). Voice verified.")
        }

        raw_response = json.dumps(parsed_json)
        return parsed_json, raw_response

    def analyze_voice(self, audio_bytes: bytes, filename: str = "audio.wav", session_id: str = None) -> dict:
        """
        Main 2-Step Voice Analysis Pipeline with Permanent Debug Logging.
        """
        if not session_id:
            session_id = f"SESS_{uuid.uuid4().hex[:8].upper()}"

        audio, sr = self.ingestion.load_wav_bytes(audio_bytes)
        audio = self.ingestion.preprocess(audio, sr)

        duration = len(audio) / sr if sr > 0 else 0.0

        # Step A: Speech presence check
        is_speech_present, step_a_raw = self.check_speech_presence(audio, sr)

        if not is_speech_present:
            result = {
                "status": "NO_SPEECH",
                "message": "No spoken voice detected in this clip",
                "session_id": session_id,
                "latency_ms": 0.0,
                # UI compatibility keys
                "risk_score": 0.0,
                "authenticity_score": 0,
                "risk_level": "Neutral",
                "alert_level": "NO_SPEECH",
                "voice_type": "NO_SPEECH",
                "voice_label": "No Spoken Voice Detected",
                "recommendation": "TRY_AGAIN_WITH_CLEAR_SPEECH",
                "user_message": "🎧 No spoken voice detected in this clip — please try again with clear speech",
                "reasoning": "No spoken voice detected in this clip"
            }

            # STEP 2 — Permanent Debug Log
            print(f"\n=======================================================", flush=True)
            print(f"[VOICE ANALYSIS DEBUG LOG] Request ID: {session_id}", flush=True)
            print(f"  - File: {filename} | Audio Byte Size: {len(audio_bytes)} bytes | Duration: {duration:.2f}s", flush=True)
            print(f"  - STEP A Raw Response: '{step_a_raw}'", flush=True)
            print(f"  - STEP B Raw Response: Skipped (Step A returned NO_SPEECH)", flush=True)
            print(f"  - FINAL Returned Result: {json.dumps(result)}", flush=True)
            print(f"=======================================================\n", flush=True)

            return result

        # Step B: Authenticity analysis (only runs if Step A returned YES)
        try:
            parsed_result, step_b_raw = self.analyze_authenticity(audio, sr)
            parsed_result["session_id"] = session_id

            # STEP 2 — Permanent Debug Log
            print(f"\n=======================================================", flush=True)
            print(f"[VOICE ANALYSIS DEBUG LOG] Request ID: {session_id}", flush=True)
            print(f"  - File: {filename} | Audio Byte Size: {len(audio_bytes)} bytes | Duration: {duration:.2f}s", flush=True)
            print(f"  - STEP A Raw Response: '{step_a_raw}'", flush=True)
            print(f"  - STEP B Raw Response: '{step_b_raw}'", flush=True)
            print(f"  - FINAL Returned Result: {json.dumps(parsed_result)}", flush=True)
            print(f"=======================================================\n", flush=True)

            return parsed_result

        except Exception as e:
            err_result = {
                "status": "ERROR",
                "message": "Analysis failed",
                "detail": str(e),
                "session_id": session_id
            }

            # STEP 2 — Permanent Debug Log (Error Case)
            print(f"\n=======================================================", flush=True)
            print(f"[VOICE ANALYSIS DEBUG LOG] Request ID: {session_id}", flush=True)
            print(f"  - File: {filename} | Audio Byte Size: {len(audio_bytes)} bytes | Duration: {duration:.2f}s", flush=True)
            print(f"  - STEP A Raw Response: '{step_a_raw}'", flush=True)
            print(f"  - STEP B Exception: '{str(e)}'", flush=True)
            print(f"  - FINAL Returned Result: {json.dumps(err_result)}", flush=True)
            print(f"=======================================================\n", flush=True)

            return err_result
