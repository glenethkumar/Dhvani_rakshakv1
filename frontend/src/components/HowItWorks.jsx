import React from 'react';
import { Cpu, ShieldCheck, PhoneCall, Mic, Layers, Activity, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      num: "01",
      title: "Audio Acquisition",
      icon: PhoneCall,
      color: "#06B6D4",
      desc: "Captures audio from Enterprise PBX Trunks (SIP G.711), In-App VoIP (WebRTC), or Speakerphone Mic mode."
    },
    {
      num: "02",
      title: "Stream Decoding & 16kHz Resampling",
      icon: Layers,
      color: "#3B82F6",
      desc: "Converts telephony codecs (G.711 µ-law / A-law) to 16kHz 16-bit PCM mono audio buffers in volatile memory."
    },
    {
      num: "03",
      title: "Acoustic AI Model (WavLM)",
      icon: Cpu,
      color: "#8B5CF6",
      desc: "Analyzes vocal tract micro-jitter, synthetic phase alignment, and neural vocoder artifacts (6.5kHz high-frequency cutoff)."
    },
    {
      num: "04",
      title: "Prosodic & Speaker Biometrics (ECAPA-TDNN)",
      icon: Activity,
      color: "#EC4899",
      desc: "Verifies vocal pitch variability, cadence, and enrolled speaker identity vectors without accessing speech text content."
    },
    {
      num: "05",
      title: "Content-Free Score Fusion Engine",
      icon: ShieldCheck,
      color: "#F59E0B",
      desc: "Combines 100% Acoustic & Biometric Voice Biomarkers into a 0-100 Risk Score. 100% privacy-preserving with zero transcript dependency."
    },
    {
      num: "06",
      title: "Human-in-the-Loop Action",
      icon: CheckCircle,
      color: "#10B981",
      desc: "GREEN (Allow) / YELLOW (Alert + Suggest Transfer) / RED (Alert + Recommend Disconnect). Auto-severing requires enterprise opt-in."
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '22px', fontWeight: '800', marginBottom: '8px', color: '#FFF' }}>
          How Dhvani Rakshak Works
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: 0, lineHeight: '1.5' }}>
          An end-to-end multi-layer AI voice clone detection and fraud deflection gateway engineered for Enterprise PBX Telecom lines, In-App VoIP, and Speakerphone mic acquisition.
        </p>
      </div>

      {/* SVG Architecture Diagram */}
      <div className="glass-panel" style={{ padding: '24px', overflowX: 'auto' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px', color: '#06B6D4' }}>
          System Processing Pipeline Diagram
        </h3>

        <svg viewBox="0 0 1000 240" style={{ width: '100%', minWidth: '700px', height: 'auto' }}>
          <defs>
            <linearGradient id="gradCyan" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06B6D4" />
              <stop offset="100%" stopColor="#3B82F6" />
            </linearGradient>
            <linearGradient id="gradRed" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#EF4444" />
              <stop offset="100%" stopColor="#DC2626" />
            </linearGradient>
          </defs>

          {/* Node 1: Ingestion */}
          <rect x="20" y="40" width="140" height="70" rx="12" fill="#0D1322" stroke="#06B6D4" strokeWidth="2" />
          <text x="90" y="70" textAnchor="middle" fill="#FFF" fontSize="13" fontWeight="bold">1. Audio Ingest</text>
          <text x="90" y="90" textAnchor="middle" fill="#9CA3AF" fontSize="10">PBX / VoIP / Mic</text>

          <path d="M 160 75 L 190 75" stroke="#06B6D4" strokeWidth="2" markerEnd="url(#arrow)" />

          {/* Node 2: Decode */}
          <rect x="195" y="40" width="140" height="70" rx="12" fill="#0D1322" stroke="#3B82F6" strokeWidth="2" />
          <text x="265" y="70" textAnchor="middle" fill="#FFF" fontSize="13" fontWeight="bold">2. Decode & Resample</text>
          <text x="265" y="90" textAnchor="middle" fill="#9CA3AF" fontSize="10">G.711 → 16kHz PCM</text>

          <path d="M 335 75 L 365 75" stroke="#3B82F6" strokeWidth="2" />

          {/* Node 3: Acoustic WavLM */}
          <rect x="370" y="15" width="140" height="55" rx="10" fill="#0D1322" stroke="#8B5CF6" strokeWidth="2" />
          <text x="440" y="40" textAnchor="middle" fill="#FFF" fontSize="12" fontWeight="bold">3A. Acoustic (WavLM)</text>
          <text x="440" y="55" textAnchor="middle" fill="#9CA3AF" fontSize="9">Deepfake Vocoder (60%)</text>

          {/* Node 3B: Whisper & Keyword */}
          <rect x="370" y="80" width="140" height="55" rx="10" fill="#0D1322" stroke="#EC4899" strokeWidth="2" />
          <text x="440" y="102" textAnchor="middle" fill="#FFF" fontSize="12" fontWeight="bold">3B. STT & Keywords</text>
          <text x="440" y="118" textAnchor="middle" fill="#9CA3AF" fontSize="9">Whisper + Gemini (40%)</text>

          <path d="M 510 42 L 545 75" stroke="#8B5CF6" strokeWidth="2" />
          <path d="M 510 108 L 545 75" stroke="#EC4899" strokeWidth="2" />

          {/* Node 4: Score Fusion */}
          <rect x="550" y="40" width="140" height="70" rx="12" fill="#0D1322" stroke="#F59E0B" strokeWidth="2" />
          <text x="620" y="70" textAnchor="middle" fill="#FFF" fontSize="13" fontWeight="bold">4. Score Fusion</text>
          <text x="620" y="90" textAnchor="middle" fill="#F59E0B" fontSize="10">Final Risk (0 - 100)</text>

          <path d="M 690 75 L 720 75" stroke="#F59E0B" strokeWidth="2" />

          {/* Node 5: Policy Check */}
          <rect x="725" y="40" width="120" height="70" rx="12" fill="#0D1322" stroke="#10B981" strokeWidth="2" />
          <text x="785" y="70" textAnchor="middle" fill="#FFF" fontSize="13" fontWeight="bold">5. Policy Check</text>
          <text x="785" y="90" textAnchor="middle" fill="#9CA3AF" fontSize="10">Human-in-Loop</text>

          <path d="M 845 75 L 875 75" stroke="#10B981" strokeWidth="2" />

          {/* Node 6: Action */}
          <rect x="880" y="40" width="100" height="70" rx="12" fill="url(#gradCyan)" />
          <text x="930" y="70" textAnchor="middle" fill="#FFF" fontSize="13" fontWeight="bold">6. Alert</text>
          <text x="930" y="90" textAnchor="middle" fill="#FFF" fontSize="10">GREEN / RED</text>
        </svg>
      </div>

      {/* Grid of 6 Steps */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat( auto-fit, minmax(280px, 1fr) )', gap: '16px' }}>
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <div
              key={step.num}
              className="glass-panel"
              style={{
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                borderLeft: `4px solid ${step.color}`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: '800', color: step.color, letterSpacing: '1px' }}>STEP {step.num}</span>
                <div style={{ padding: '8px', borderRadius: '8px', background: `${step.color}20`, color: step.color }}>
                  <Icon size={18} />
                </div>
              </div>
              <h4 style={{ fontSize: '15px', fontWeight: '700', margin: 0, color: '#FFF' }}>{step.title}</h4>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0, lineHeight: '1.4' }}>{step.desc}</p>
            </div>
          );
        })}
      </div>

    </div>
  );
}
