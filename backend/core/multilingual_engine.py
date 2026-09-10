"""
Dhvani Rakshak - Multilingual & Dialect Adaptation Engine (India-Focused)
Enhanced with Neural Acoustic Language Identification (LID).
Supports Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Bengali, Gujarati, and Indian English.
Adjusts prosodic thresholds dynamically to prevent false positive alerts for regional accents.
"""

import sys
import os
import numpy as np

# Ensure models can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.language_id_model import LanguageIdModel


class MultilingualEngine:
    SUPPORTED_LANGUAGES = {
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "mr": "Marathi",
        "bn": "Bengali",
        "gu": "Gujarati",
        "en-IN": "Indian English"
    }

    # Prosodic baseline adjustments per language group
    LANGUAGE_PROFILES = {
        "hi": {"f0_std_multiplier": 1.0, "pitch_range_tolerance": 1.0, "pause_tolerance": 1.0},
        "ta": {"f0_std_multiplier": 0.82, "pitch_range_tolerance": 1.25, "pause_tolerance": 1.15},
        "te": {"f0_std_multiplier": 0.85, "pitch_range_tolerance": 1.20, "pause_tolerance": 1.10},
        "kn": {"f0_std_multiplier": 0.88, "pitch_range_tolerance": 1.18, "pause_tolerance": 1.08},
        "ml": {"f0_std_multiplier": 0.80, "pitch_range_tolerance": 1.28, "pause_tolerance": 1.20},
        "mr": {"f0_std_multiplier": 0.95, "pitch_range_tolerance": 1.05, "pause_tolerance": 1.02},
        "bn": {"f0_std_multiplier": 0.90, "pitch_range_tolerance": 1.10, "pause_tolerance": 1.05},
        "gu": {"f0_std_multiplier": 0.92, "pitch_range_tolerance": 1.08, "pause_tolerance": 1.04},
        "en-IN": {"f0_std_multiplier": 1.0, "pitch_range_tolerance": 1.0, "pause_tolerance": 1.0}
    }

    def __init__(self, default_lang: str = "en-IN"):
        self.current_language = default_lang
        self.lid = LanguageIdModel()

    def set_language(self, lang_code: str):
        if lang_code in self.SUPPORTED_LANGUAGES:
            self.current_language = lang_code
            return True
        return False

    def identify_language_acoustic(self, audio: np.ndarray) -> dict:
        """Run acoustic LID neural forward pass on audio frames."""
        return self.lid.identify_language(audio)

    def adapt_prosodic_scores(self, prosody_res: dict, lang_code: str = None, audio: np.ndarray = None) -> dict:
        """Apply language dialect calibration to prosodic anomaly score."""
        if (not lang_code or lang_code == "auto") and audio is not None and len(audio) > 512:
            lid_res = self.identify_language_acoustic(audio)
            target_lang = lid_res["detected_code"]
            prosody_res["lid_confidence"] = lid_res["confidence"]
            prosody_res["lid_probabilities"] = lid_res["probabilities"]
        else:
            target_lang = lang_code if lang_code in self.SUPPORTED_LANGUAGES else self.current_language

        profile = self.LANGUAGE_PROFILES.get(target_lang, self.LANGUAGE_PROFILES["en-IN"])
        raw_score = prosody_res.get("prosody_anomaly_score", 0.0)

        # Calibrate pitch std & rhythm based on regional language features
        calibrated_score = raw_score * (1.0 / profile["pitch_range_tolerance"])

        # If natural rapid cadence in Dravidian languages, suppress false pause alerts
        if target_lang in ["ta", "te", "kn", "ml"]:
            calibrated_score *= 0.88

        adjusted_score = round(max(0.0, min(1.0, calibrated_score)), 4)
        prosody_res["calibrated_prosody_score"] = adjusted_score
        prosody_res["detected_language"] = self.SUPPORTED_LANGUAGES[target_lang]
        prosody_res["language_code"] = target_lang
        return prosody_res
