import sys
import os
import urllib.request
import json
import asyncio
import websockets

sys.stdout.reconfigure(encoding='utf-8')

def test_http_health():
    url = "http://localhost:8000/api/v1/health"
    try:
        req = urllib.request.urlopen(url, timeout=3)
        status = req.getcode()
        body = json.loads(req.read().decode('utf-8'))
        print(f"HTTP Health Check Status: {status}")
        print(f"Health Response: {json.dumps(body, indent=2)}")
        return status == 200
    except Exception as e:
        print(f"HTTP Health Check Failed: {e}")
        return False

async def test_websocket_stream():
    uri = "ws://localhost:8000/ws/live-stream"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket Connection Successfully Opened!")
            
            import numpy as np
            import struct
            
            sample_rate = 16000
            duration = 1.0
            num_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, num_samples, False)
            sine_wave = np.sin(2 * np.pi * 440 * t) * 0.5
            pcm_data = (sine_wave * 32767).astype(np.int16).tobytes()
            
            # WAV Header
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
            
            await websocket.send(wav_bytes)
            print("Sent 1.0s test audio payload over WebSocket...")
            
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            payload = json.loads(response)
            print("\nReceived WebSocket Response Payload from Backend:")
            print(json.dumps(payload, indent=2))
            return True
    except Exception as e:
        print(f"WebSocket Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("=== TESTING BACKEND & FRONTEND INTEGRATION ===")
    http_ok = test_http_health()
    ws_ok = asyncio.run(test_websocket_stream())
    print("\n=== VERIFICATION SUMMARY ===")
    print(f"Backend HTTP API: {'WORKING' if http_ok else 'FAILED'}")
    print(f"Backend WebSocket Stream: {'WORKING' if ws_ok else 'FAILED'}")
