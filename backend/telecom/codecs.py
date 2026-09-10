"""
Dhvani Rakshak - Telephony Audio Codecs & Stream Processing Layer
Implements G.711 mu-law (PCMU) and A-law (PCMA) decoding, 8kHz to 16kHz
band-limited resampling, and PSTN/cellular acoustic channel simulation.
Zero external C-dependency implementation compatible with Python 3.14+.
"""

import numpy as np
import scipy.signal as signal


# ---------------------------------------------------------------------------
# G.711 mu-law (PCMU) and A-law (PCMA) Precomputed 8-bit to 16-bit Tables
# ---------------------------------------------------------------------------
def _build_mulaw_table() -> np.ndarray:
    """Build G.711 mu-law 8-bit byte to 16-bit signed linear PCM lookup table."""
    table = np.zeros(256, dtype=np.int16)
    for b in range(256):
        inverted = ~b & 0xFF
        sign = inverted & 0x80
        exponent = (inverted >> 4) & 0x07
        mantissa = inverted & 0x0F
        sample = ((mantissa << 3) + 0x84) << exponent
        sample -= 0x84
        table[b] = -sample if sign != 0 else sample
    return table


def _build_alaw_table() -> np.ndarray:
    """Build G.711 A-law 8-bit byte to 16-bit signed linear PCM lookup table."""
    table = np.zeros(256, dtype=np.int16)
    for b in range(256):
        inverted = b ^ 0x55
        sign = inverted & 0x80
        exponent = (inverted >> 4) & 0x07
        mantissa = inverted & 0x0F
        if exponent == 0:
            sample = (mantissa << 4) + 8
        else:
            sample = ((mantissa << 4) + 0x108) << (exponent - 1)
        table[b] = -sample if sign != 0 else sample
    return table


# Precompute lookup tables once for nanosecond lookups
MULAW_TO_PCM16_TABLE = _build_mulaw_table()
ALAW_TO_PCM16_TABLE = _build_alaw_table()


def decode_mulaw_to_pcm(raw_mulaw_bytes: bytes) -> np.ndarray:
    """
    Decode G.711 mu-law raw byte buffer (RFC 3551 PT 0) to float32 linear PCM (-1.0 to 1.0).
    Input: standard 8000 Hz, 8-bit mu-law telephony audio.
    Output: 1D numpy array of float32 samples.
    """
    byte_indices = np.frombuffer(raw_mulaw_bytes, dtype=np.uint8)
    pcm16 = MULAW_TO_PCM16_TABLE[byte_indices]
    return (pcm16.astype(np.float32) / 32768.0).astype(np.float32)


def decode_alaw_to_pcm(raw_alaw_bytes: bytes) -> np.ndarray:
    """
    Decode G.711 A-law raw byte buffer (RFC 3551 PT 8) to float32 linear PCM (-1.0 to 1.0).
    Input: standard 8000 Hz, 8-bit A-law telephony audio.
    Output: 1D numpy array of float32 samples.
    """
    byte_indices = np.frombuffer(raw_alaw_bytes, dtype=np.uint8)
    pcm16 = ALAW_TO_PCM16_TABLE[byte_indices]
    return (pcm16.astype(np.float32) / 32768.0).astype(np.float32)


def encode_pcm_to_mulaw(pcm_samples: np.ndarray) -> bytes:
    """
    Encode float32 linear PCM (-1.0 to 1.0) into G.711 mu-law 8-bit bytes.
    Used for generating simulated inbound carrier audio.
    """
    scaled = np.clip(pcm_samples * 32767.0, -32768, 32767).astype(np.int32)
    mu_bytes = bytearray(len(scaled))
    bias = 0x84
    clip = 32635

    for i, val in enumerate(scaled):
        sign = 0x80 if val < 0 else 0
        if val < 0:
            val = -val
        val = min(val, clip) + bias
        exponent = 7
        for exp in range(7, -1, -1):
            if val >= (0x80 << exp):
                exponent = exp
                break
        mantissa = (val >> (exponent + 3)) & 0x0F
        mu_bytes[i] = ~(sign | (exponent << 4) | mantissa) & 0xFF

    return bytes(mu_bytes)


def resample_telephony_to_16k(audio_8k: np.ndarray, source_rate: int = 8000, target_rate: int = 16000) -> np.ndarray:
    """
    Resample 8kHz telephony audio to 16kHz standard for AASIST & ECAPA-TDNN neural engines.
    Uses polyphase band-limited anti-aliasing interpolation.
    """
    if len(audio_8k) == 0:
        return np.zeros(0, dtype=np.float32)
    
    if source_rate == target_rate:
        return audio_8k.astype(np.float32)

    num_target_samples = int(round(len(audio_8k) * float(target_rate) / float(source_rate)))
    resampled = signal.resample(audio_8k, num_target_samples)
    return np.clip(resampled, -1.0, 1.0).astype(np.float32)


def apply_telephony_channel_degradation(audio_16k: np.ndarray) -> np.ndarray:
    """
    Simulate real PSTN / 2G / 3G / VoLTE mobile telephony degradation:
    1. 300Hz to 3400Hz standard G.712 telephone bandpass filter
    2. Quantization companding noise
    3. Mild line impedance and mobile network hiss
    Ensures models are stress-tested against realistic call center conditions.
    """
    if len(audio_16k) < 128:
        return audio_16k

    # 4th-order Butterworth bandpass (300Hz - 3400Hz)
    sos = signal.butter(4, [300.0, 3400.0], btype='bandpass', fs=16000, output='sos')
    filtered = signal.sosfilt(sos, audio_16k)

    # Simulated G.711 8-bit companding quantization step
    quantized = np.round(filtered * 128.0) / 128.0

    # Mild telephony thermal noise floor (-45 dB SNR)
    np.random.seed(len(audio_16k) % 1000)
    noise = np.random.normal(0, 0.0004, len(quantized))
    degraded = np.clip(quantized + noise, -1.0, 1.0)
    return degraded.astype(np.float32)
