import React, { useEffect, useRef, useState } from 'react';
import { ShieldCheck, Zap, Radio, PhoneCall, PhoneOff, Mic, AlertTriangle } from 'lucide-react';
import { WS_BASE_URL, encodeWAV } from '../utils/audioEncoder';

export default function LiveMonitor() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [measuredLatency, setMeasuredLatency] = useState(142.5);
  const [streamError, setStreamError] = useState(null);

  const [activeCall, setActiveCall] = useState({
    sessionId: "SESS_98F21A0C",
    callerId: "+91 98765 43210 (Rajesh Sharma - CEO)",
    location: "Mumbai, MH (Trusted Device)",
    language: "Indian English (en-IN)",
    riskScore: 28.4,
    alertLevel: "GREEN",
    recommendation: "AUTHENTIC_VOICE_ALLOWED",
    ttsSignatures: { ElevenLabs: 0.12, OpenAI_Voice: 0.08, Google_TTS: 0.05 },
    mfccVar: 14.8,
    pitchHz: 142.5,
    jitterPct: 0.42,
    phaseSmoothness: 3.12
  });

  const [callLogs, setCallLogs] = useState([
    { id: 1, time: "05:32:10", callId: "+91 98765 43210", score: 28.4, level: "GREEN", status: "AUTHENTICATED" },
    { id: 2, time: "05:30:45", callId: "+91 98111 88200", score: 88.5, level: "RED", status: "AI CLONE BLOCKED" },
    { id: 3, time: "05:28:12", callId: "+91 99203 11049", score: 72.1, level: "YELLOW", status: "OTP STEP-UP VERIFIED" },
    { id: 4, time: "05:22:04", callId: "+91 97120 44921", score: 18.2, level: "GREEN", status: "AUTHENTICATED" }
  ]);

  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const analyserRef = useRef(null);
  const processorRef = useRef(null);

  // Stop Streaming helper
  const stopLiveStream = () => {
    setIsStreaming(false);
    setWsConnected(false);

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(t => t.stop());
      mediaStreamRef.current = null;
    }
  };

  // Start Live Microphone Streaming over WebSockets
  const startLiveStream = async () => {
    setStreamError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }
      });
      mediaStreamRef.current = stream;

      const audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      audioContextRef.current = audioCtx;

      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 512;
      analyserRef.current = analyser;

      // ScriptProcessor for 250ms chunks (4096 samples at 16kHz is ~256ms)
      const processor = audioCtx.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      source.connect(analyser);
      analyser.connect(processor);
      processor.connect(audioCtx.destination);

      // Open WebSocket connection
      const wsUrl = `${WS_BASE_URL.replace(/^http/, 'ws')}/ws/live-stream`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        setWsConnected(true);
        setIsStreaming(true);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload) {
            setMeasuredLatency(payload.latency_ms || 140.0);
            setActiveCall(prev => ({
              ...prev,
              sessionId: payload.session_id || prev.sessionId,
              riskScore: payload.risk_score !== undefined ? payload.risk_score : prev.riskScore,
              alertLevel: payload.alert_level || prev.alertLevel,
              recommendation: payload.recommendation || prev.recommendation,
              ttsSignatures: payload.tts_signatures || prev.ttsSignatures,
              acousticAnomaly: payload.acoustic_anomaly || 0.1,
              prosodyAnomaly: payload.prosody_anomaly || 0.1
            }));

            // If score is alarming, push to top of log
            if (payload.risk_score >= 60) {
              const nowStr = new Date().toTimeString().split(' ')[0];
              setCallLogs(prev => [
                {
                  id: Date.now(),
                  time: nowStr,
                  callId: "Live Mic Stream",
                  score: payload.risk_score,
                  level: payload.alert_level,
                  status: payload.alert_level === 'RED' ? 'AI CLONE BLOCKED' : 'OTP STEP-UP CHALLENGE'
                },
                ...prev.slice(0, 9)
              ]);
            }
          }
        } catch (e) {
          // ignore non-json
        }
      };

      ws.onerror = () => {
        setStreamError("WebSocket connection failed. Falling back to local audio visualizer.");
        setWsConnected(false);
      };

      ws.onclose = () => {
        setWsConnected(false);
      };

      // Stream chunks every buffer process
      processor.onaudioprocess = (e) => {
        if (!ws || ws.readyState !== WebSocket.OPEN) return;
        const inputData = e.inputBuffer.getChannelData(0);
        const wavBlob = encodeWAV(inputData, 16000);

        wavBlob.arrayBuffer().then(buf => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(buf);
          }
        });
      };

      setIsStreaming(true);

    } catch (err) {
      setStreamError("Microphone access failed: " + err.message + ". You can use the Attack Simulation button.");
      setIsStreaming(false);
      setWsConnected(false);
    }
  };

  // Toggle demo attack state
  const handleSimulateAttack = () => {
    const isNowRed = activeCall.alertLevel !== 'RED';
    setActiveCall(prev => ({
      ...prev,
      sessionId: `SESS_${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      alertLevel: isNowRed ? 'RED' : 'GREEN',
      riskScore: isNowRed ? 91.2 : 24.8,
      recommendation: isNowRed ? 'BLOCK_AI_CLONE_TRANSFER' : 'AUTHENTIC_VOICE_ALLOWED',
      ttsSignatures: isNowRed
        ? { ElevenLabs: 0.94, OpenAI_Voice: 0.18, Google_TTS: 0.05 }
        : { ElevenLabs: 0.08, OpenAI_Voice: 0.04, Google_TTS: 0.02 },
      pitchHz: isNowRed ? 112.0 : 142.5,
      jitterPct: isNowRed ? 0.04 : 0.42,
      phaseSmoothness: isNowRed ? 1.35 : 3.12
    }));

    if (isNowRed) {
      setCallLogs(prev => [
        {
          id: Date.now(),
          time: new Date().toTimeString().split(' ')[0],
          callId: "+91 98111 88200 (Simulated Attack)",
          score: 91.2,
          level: "RED",
          status: "AI CLONE BLOCKED IN 140ms"
        },
        ...prev
      ]);
    }
  };

  // Real-time Canvas Waveform Visualizer
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.lineWidth = 2;

      // Draw subtle background grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.beginPath();
      for (let x = 0; x < canvas.width; x += 30) {
        ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height);
      }
      for (let y = 0; y < canvas.height; y += 20) {
        ctx.moveTo(0, y); ctx.lineTo(canvas.width, y);
      }
      ctx.stroke();

      const height = canvas.height;
      const width = canvas.width;
      const mid = height / 2;

      ctx.strokeStyle = activeCall.alertLevel === 'RED' ? '#EF4444' : activeCall.alertLevel === 'YELLOW' ? '#F59E0B' : '#10B981';
      ctx.shadowColor = ctx.strokeStyle;
      ctx.shadowBlur = 10;
      ctx.beginPath();

      // If live microphone analyser is active, draw real time-domain samples
      if (analyserRef.current && isStreaming) {
        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserRef.current.getByteTimeDomainData(dataArray);

        const sliceWidth = width / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const v = dataArray[i] / 128.0;
          const y = v * (height / 2);

          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);

          x += sliceWidth;
        }
      } else {
        // Fallback smooth harmonic wave
        for (let x = 0; x < width; x++) {
          const freq1 = 0.03;
          const freq2 = 0.08;
          const amp = activeCall.alertLevel === 'RED' ? 38 : 22;
          const y = mid + Math.sin(x * freq1 + phase) * amp + Math.cos(x * freq2 + phase * 1.5) * (amp * 0.4);
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        phase += 0.08;
      }

      ctx.stroke();
      ctx.shadowBlur = 0;
      animationFrameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [activeCall, isStreaming]);

  const getAlertBadgeClass = (level) => {
    if (level === 'RED') return 'bg-red-500/20 text-red-400 border-red-500/50 glow-red';
    if (level === 'YELLOW') return 'bg-amber-500/20 text-amber-400 border-amber-500/50';
    return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50 glow-green';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Header Banner */}
      <div className="glass-panel" style={{ padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', background: 'rgba(6, 182, 212, 0.15)', borderRadius: '12px', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
            <Radio size={28} color="#06B6D4" className={isStreaming ? "animate-pulse" : ""} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '700', margin: 0, letterSpacing: '-0.5px' }}>Live Call Stream Interceptor</h2>
              <span style={{
                fontSize: '11px', padding: '3px 10px', borderRadius: '20px',
                background: wsConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                color: wsConnected ? '#10B981' : '#F59E0B',
                border: `1px solid ${wsConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                fontWeight: '700'
              }}>
                {wsConnected ? '● Live WebSocket Stream' : '○ Standby Monitor'}
              </span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
              <strong>What it does:</strong> Checks live audio streams in real time. It analyzes pitch and voice quality to spot fake AI voices instantly.
            </p>
          </div>
        </div>

        {/* Streaming Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '20px', fontSize: '12px', color: '#10B981' }}>
            <ShieldCheck size={14} /> Zero Audio Storage Verified
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '20px', fontSize: '12px', color: '#06B6D4' }}>
            <Zap size={14} /> Latency: {measuredLatency}ms
          </div>

          {isStreaming ? (
            <button
              onClick={stopLiveStream}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 18px', borderRadius: '20px',
                background: '#EF4444', color: '#FFF', fontWeight: '700', border: 'none', cursor: 'pointer', fontSize: '13px',
                boxShadow: '0 2px 10px rgba(239, 68, 68, 0.4)'
              }}
            >
              <PhoneOff size={14} /> Stop Mic Stream
            </button>
          ) : (
            <button
              onClick={startLiveStream}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 18px', borderRadius: '20px',
                background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)', color: '#FFF', fontWeight: '700',
                border: 'none', cursor: 'pointer', fontSize: '13px', boxShadow: '0 2px 10px rgba(16, 185, 129, 0.3)'
              }}
            >
              <Mic size={14} /> Connect Live Mic Stream
            </button>
          )}

          <button
            onClick={handleSimulateAttack}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', borderRadius: '20px',
              background: 'rgba(255, 255, 255, 0.08)', color: '#FFF', fontWeight: '700',
              border: '1px solid rgba(255, 255, 255, 0.18)', cursor: 'pointer', fontSize: '12px'
            }}
          >
            {activeCall.alertLevel === 'RED' ? 'Reset to Safe' : 'Simulate AI Attack'}
          </button>
        </div>
      </div>

      {streamError && (
        <div style={{ padding: '14px 20px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.12)', border: '1px solid #EF4444', color: '#EF4444', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AlertTriangle size={18} />
          <span>{streamError}</span>
        </div>
      )}

      {/* Visual Security Banner Graphic */}
      <div className="image-banner-card" style={{ height: '220px', position: 'relative' }}>
        <img 
          src="/images/feature_monitor.jpg" 
          onError={(e) => { e.currentTarget.src = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80"; }} 
          alt="Live Call Interceptor SOC Shield" 
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(7, 9, 14, 0.2) 0%, rgba(7, 9, 14, 0.85) 100%)',
          display: 'flex', alignItems: 'flex-end', padding: '24px'
        }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: '800', color: '#06B6D4', textTransform: 'uppercase', letterSpacing: '1px' }}>
              🛡️ Active Voice Shield Protection
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: '800', color: '#FFF', margin: '4px 0' }}>
              Real-Time Banking & Voice Call Interception
            </h3>
            <p style={{ fontSize: '12px', color: '#D1D5DB', margin: 0 }}>
              Analyzing incoming caller pitch variance, STFT phase alignment, and biometric voice embeddings on the fly.
            </p>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Monitor + Right Risk Meter */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
        
        {/* Oscilloscope Waveform & Acoustic Stats */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <PhoneCall size={18} color="#06B6D4" />
              <span style={{ fontWeight: '600', fontSize: '15px' }}>Active Session: {activeCall.sessionId}</span>
            </div>
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{activeCall.callerId}</span>
          </div>

          {/* Canvas Waveform Visualizer */}
          <div style={{ background: '#05070D', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.1)', padding: '16px', position: 'relative' }}>
            <canvas ref={canvasRef} width={650} height={160} style={{ width: '100%', height: '160px', display: 'block' }} />
            <div style={{ position: 'absolute', top: '12px', right: '16px', fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
              {isStreaming ? "LIVE MIC OSCILLOSCOPE (16kHz PCM)" : "SPECTRAL STFT PHASE MONITOR"}
            </div>
          </div>

          {/* Feature Metric Tiles */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>VOICE NATURALNESS</div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: activeCall.mfccVar < 10 ? '#EF4444' : '#F3F4F6' }}>
                {activeCall.mfccVar > 10 ? "Organic" : "Synthetic"}
              </div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>VOICE PITCH</div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: '#06B6D4' }}>
                {activeCall.pitchHz} Hz
              </div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>PITCH VARIATION</div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: activeCall.jitterPct < 0.15 ? '#EF4444' : '#10B981' }}>
                {activeCall.jitterPct}%
              </div>
            </div>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>ACOUSTIC CLARITY</div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: activeCall.phaseSmoothness < 2.0 ? '#F59E0B' : '#10B981' }}>
                {activeCall.phaseSmoothness}
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Risk Meter & TTS Generator Signature Probabilities */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '600', width: '100%', textAlign: 'left', margin: 0 }}>Impersonation Risk Gauge</h3>

          {/* Circular Risk Score Display */}
          <div style={{ position: 'relative', width: '150px', height: '150px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="150" height="150" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" stroke="rgba(255, 255, 255, 0.1)" strokeWidth="10" fill="none" />
              <circle
                cx="50" cy="50" r="42"
                stroke={activeCall.alertLevel === 'RED' ? '#EF4444' : activeCall.alertLevel === 'YELLOW' ? '#F59E0B' : '#10B981'}
                strokeWidth="10" fill="none"
                strokeDasharray="264"
                strokeDashoffset={264 - (264 * activeCall.riskScore) / 100}
                strokeLinecap="round"
                transform="rotate(-90 50 50)"
                style={{ transition: 'stroke-dashoffset 0.5s ease' }}
              />
            </svg>
            <div style={{ position: 'absolute', textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: '800', lineHeight: '1', color: activeCall.alertLevel === 'RED' ? '#EF4444' : activeCall.alertLevel === 'YELLOW' ? '#F59E0B' : '#10B981' }}>
                {activeCall.riskScore}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>SCORE / 100</div>
            </div>
          </div>

          <div style={{ padding: '6px 16px', borderRadius: '20px', fontSize: '13px', fontWeight: '700', letterSpacing: '0.5px', border: '1px solid' }} className={getAlertBadgeClass(activeCall.alertLevel)}>
            {activeCall.alertLevel === 'WAITING' ? 'WAITING FOR SPEECH' : activeCall.alertLevel === 'GREEN' ? 'AUTHENTIC VOICE' : activeCall.alertLevel === 'YELLOW' ? 'SUSPECTED ANOMALY' : 'HIGH RISK AI CLONE'}
          </div>

          {/* TTS Signature Progress Bars */}
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '4px' }}>TTS ENGINE SIGNATURES</div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '2px' }}>
                <span>ElevenLabs</span>
                <span style={{ fontWeight: '700', color: activeCall.ttsSignatures.ElevenLabs > 0.5 ? '#EF4444' : '#06B6D4' }}>
                  {(activeCall.ttsSignatures.ElevenLabs * 100).toFixed(0)}%
                </span>
              </div>
              <div style={{ height: '5px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${activeCall.ttsSignatures.ElevenLabs * 100}%`, height: '100%', background: activeCall.ttsSignatures.ElevenLabs > 0.5 ? '#EF4444' : '#06B6D4' }} />
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '2px' }}>
                <span>OpenAI Voice</span>
                <span style={{ fontWeight: '700', color: activeCall.ttsSignatures.OpenAI_Voice > 0.5 ? '#EF4444' : '#F59E0B' }}>
                  {(activeCall.ttsSignatures.OpenAI_Voice * 100).toFixed(0)}%
                </span>
              </div>
              <div style={{ height: '5px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${activeCall.ttsSignatures.OpenAI_Voice * 100}%`, height: '100%', background: activeCall.ttsSignatures.OpenAI_Voice > 0.5 ? '#EF4444' : '#F59E0B' }} />
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Real-Time Call Event Stream Log Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>Live Intercept Log Feed</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px' }}>TIMESTAMP</th>
                <th style={{ padding: '10px' }}>CALLER IDENTITY</th>
                <th style={{ padding: '10px' }}>RISK SCORE</th>
                <th style={{ padding: '10px' }}>ALERT TIER</th>
                <th style={{ padding: '10px' }}>DECISION WORKFLOW</th>
              </tr>
            </thead>
            <tbody>
              {callLogs.map((log) => (
                <tr key={log.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                  <td style={{ padding: '12px 10px', fontFamily: 'monospace' }}>{log.time}</td>
                  <td style={{ padding: '12px 10px', fontWeight: '500' }}>{log.callId}</td>
                  <td style={{ padding: '12px 10px', fontWeight: '700', color: log.score >= 80 ? '#EF4444' : log.score >= 60 ? '#F59E0B' : '#10B981' }}>{log.score}</td>
                  <td style={{ padding: '12px 10px' }}>
                    <span style={{ padding: '3px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700' }} className={getAlertBadgeClass(log.level)}>
                      {log.level}
                    </span>
                  </td>
                  <td style={{ padding: '12px 10px', color: 'var(--text-muted)' }}>{log.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
