/**
 * Dhvani Rakshak - Browser Audio Utilities
 * Encodes Float32Array PCM samples into standard 16kHz mono RIFF/WAV blobs.
 */

export function encodeWAV(samples, sampleRate = 16000) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  /* RIFF identifier */
  writeString(view, 0, 'RIFF');
  /* file length */
  view.setUint32(4, 36 + samples.length * 2, true);
  /* RIFF type */
  writeString(view, 8, 'WAVE');
  /* format chunk identifier */
  writeString(view, 12, 'fmt ');
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (raw PCM) */
  view.setUint16(20, 1, true);
  /* channel count (1 = mono) */
  view.setUint16(22, 1, true);
  /* sample rate */
  view.setUint32(24, sampleRate, true);
  /* byte rate (sampleRate * blockAlign) */
  view.setUint32(28, sampleRate * 2, true);
  /* block align (channelCount * bytesPerSample) */
  view.setUint16(32, 2, true);
  /* bits per sample */
  view.setUint16(34, 16, true);
  /* data chunk identifier */
  writeString(view, 36, 'data');
  /* data chunk length */
  view.setUint32(40, samples.length * 2, true);

  /* Write 16-bit PCM samples with clamping */
  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }

  return new Blob([view], { type: 'audio/wav' });
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

/**
 * Resample Float32Array from sourceSampleRate to targetSampleRate using linear interpolation
 */
export function resampleAudio(audioBuffer, sourceSampleRate, targetSampleRate = 16000) {
  if (sourceSampleRate === targetSampleRate) {
    return audioBuffer;
  }
  const ratio = sourceSampleRate / targetSampleRate;
  const newLength = Math.round(audioBuffer.length / ratio);
  const result = new Float32Array(newLength);
  
  for (let i = 0; i < newLength; i++) {
    const origIndex = i * ratio;
    const index1 = Math.floor(origIndex);
    const index2 = Math.min(index1 + 1, audioBuffer.length - 1);
    const fraction = origIndex - index1;
    result[i] = audioBuffer[index1] * (1 - fraction) + audioBuffer[index2] * fraction;
  }
  return result;
}

/**
 * API Base URL helper supporting mobile device IP, Render production URL, or local fallback
 */
function resolveBackendUrls() {
  if (typeof window === 'undefined') {
    return {
      api: 'http://localhost:8000',
      ws: 'ws://localhost:8000'
    };
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;

  // 1. Explicit environment variables
  if (import.meta.env.VITE_API_URL) {
    const api = import.meta.env.VITE_API_URL;
    const ws = api.replace(/^http/, 'ws');
    return { api, ws };
  }

  // 2. Production Vercel deployment (Same Origin serverless endpoint)
  if (hostname.includes('vercel.app') || hostname.includes('onrender.com') || hostname.includes('github.io')) {
    return {
      api: import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : ''),
      ws: import.meta.env.VITE_WS_URL || (typeof window !== 'undefined' ? `wss://${hostname}` : '')
    };
  }

  // 3. Local Wi-Fi Network access from mobile devices (e.g. 192.168.x.x)
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return {
      api: `http://${hostname}:8000`,
      ws: `ws://${hostname}:8000`
    };
  }

  // 4. Default Localhost Development
  return {
    api: 'http://localhost:8000',
    ws: 'ws://localhost:8000'
  };
}

const resolvedUrls = resolveBackendUrls();
export const API_BASE_URL = resolvedUrls.api;
export const WS_BASE_URL = resolvedUrls.ws;

