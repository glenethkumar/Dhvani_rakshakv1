import sys
sys.path.append("backend")
from core.acoustic_analyzer import AcousticAnalyzer
from test_voice_conversion_direct import generate_voice_converted_ai_clip

ac = AcousticAnalyzer()
audio = generate_voice_converted_ai_clip()

ac_res = ac.detect_tts_artifacts(audio)
print("Acoustic Results:")
print("  Spectral Features:", ac_res["spectral_features"])
print("  MFCC Variance:", ac_res["mfcc_variance"])
print("  Splicing Discontinuity:", ac_res["splicing_discontinuity"])
print("  Neural Deepfake Prob:", ac_res["neural_deepfake_probability"])
print("  Acoustic Anomaly Score:", ac_res["acoustic_anomaly_score"])
