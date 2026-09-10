"""
Dhvani Rakshak - Deep Learning Models Package
Exposes AASIST/RawNet2 Anti-Spoofing, ECAPA-TDNN Speaker Verification, and Language ID neural engines.
"""

from .deep_fake_detector import DeepFakeDetector
from .ecapa_tdnn_verifier import EcapaTdnnVerifier
from .language_id_model import LanguageIdModel

__all__ = ["DeepFakeDetector", "EcapaTdnnVerifier", "LanguageIdModel"]
