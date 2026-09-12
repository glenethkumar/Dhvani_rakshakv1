import requests
import numpy as np
import struct
import json

def test_analyze_endpoint():
    url = "http://localhost:8000/analyze"
    sample_rate = 16000
    duration = 5.0
    num_samples = int(sample_rate * duration)
    
    # Generate 5.0s human-like voice tone (440Hz with 10Hz pitch modulation)
    t = np.linspace(0, duration, num_samples, False)
    freq = 150 + 15 * np.sin(2 * np.pi * 3 * t)  # pitch variation
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    sine_wave = np.sin(phase) * 0.4
    pcm_data = (sine_wave * 32767).astype(np.int16).tobytes()
    
    # Build 16kHz mono WAV header
    header = bytearray()
    header.extend(b'RIFF')
    header.extend(struct.pack('<I', 36 + len(pcm_data)))
    header.extend(b'WAVEfmt ')
    header.extend(struct.pack('<I', 16))
    header.extend(struct.pack('<H', 1))  # PCM
    header.extend(struct.pack('<H', 1))  # mono
    header.extend(struct.pack('<I', sample_rate))
    header.extend(struct.pack('<I', sample_rate * 2))
    header.extend(struct.pack('<H', 2))
    header.extend(struct.pack('<H', 16))
    header.extend(b'data')
    header.extend(struct.pack('<I', len(pcm_data)))
    wav_bytes = bytes(header + pcm_data)

    files = {'file': ('live_mic_5s.wav', wav_bytes, 'audio/wav')}
    data = {
        'language': 'en-IN',
        'caller_metadata_json': json.dumps({'caller_id': 'Live Mic Capture'})
    }

    try:
        response = requests.post(url, files=files, data=data, timeout=5)
        print("Analyze HTTP Status Code:", response.status_code)
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print("Analyze request failed:", e)
        return False

if __name__ == "__main__":
    test_analyze_endpoint()
