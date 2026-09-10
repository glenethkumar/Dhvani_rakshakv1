import React, { useState, useEffect } from 'react';
import { Eye, CheckCircle2, AlertTriangle, HelpCircle, RefreshCw } from 'lucide-react';
import { API_BASE_URL } from '../utils/audioEncoder';

export default function ExplainabilityDashboard() {
  const [selectedCase, setSelectedCase] = useState("elevenlabs");
  const [loading, setLoading] = useState(false);
  const [isLiveApi, setIsLiveApi] = useState(false);
  const [liveExplanation, setLiveExplanation] = useState(null);

  const fallbackCases = {
    elevenlabs: {
      id: "CALL_SESSION_88190",
      score: 88.5,
      verdict: "BLOCKED FAKE VOICE",
      reasons: [
        "1. Sound Quality: High-frequency neural vocoder patterns matching ElevenLabs AI generator above 6.5kHz.",
        "2. Speaking Pattern: Voice pitch is artificially flat (0.04% jitter vs normal human variation 0.20%-1.20%).",
        "3. Missing Breathing: Zero natural breathing pauses detected between conversational sentences.",
        "4. Voice Sample Match: Cosine similarity distance > 0.62 from enrolled CEO voice print."
      ],
      breakdown: { soundQuality: "35%", speakingStyle: "27%", voiceMatch: "26%" },
      ruleCheck: "Blocked under Official Financial Safety Rules (RBI Cyber Security Guidelines 2023 & GDPR)."
    },
    genuine: {
      id: "CALL_SESSION_10492",
      score: 28.4,
      verdict: "SAFE REAL VOICE",
      reasons: [
        "1. Sound Quality: Natural human spectral envelope with healthy harmonic formants (F1-F3).",
        "2. Speaking Pattern: Natural pitch contour variation (24.8 Hz dynamic range) and micro-vibration.",
        "3. Natural Breathing: Physiological breathing pauses detected normally.",
        "4. Voice Sample Match: 94.2% cosine similarity match with enrolled CEO voice profile."
      ],
      breakdown: { soundQuality: "11%", speakingStyle: "10%", voiceMatch: "7%" },
      ruleCheck: "Verified safe under standard caller biometric authentication policy."
    }
  };

  const fetchLiveExplanation = async (caseType) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("case_type", caseType);
      const res = await fetch(`${API_BASE_URL}/api/v1/explain`, {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setLiveExplanation(data);
        setIsLiveApi(true);
      } else {
        setIsLiveApi(false);
      }
    } catch (err) {
      setIsLiveApi(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveExplanation(selectedCase);
  }, [selectedCase]);

  const curr = fallbackCases[selectedCase];
  const displayedReasons = (liveExplanation && liveExplanation.explanation && liveExplanation.explanation.reasons) 
    ? liveExplanation.explanation.reasons 
    : curr.reasons;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <h2 style={{ fontSize: '22px', fontWeight: '700', margin: 0 }}>Explainable AI & Forensic Reasoning (XAI)</h2>
            <span style={{
              fontSize: '11px', padding: '3px 10px', borderRadius: '20px',
              background: isLiveApi ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              color: isLiveApi ? '#10B981' : '#F59E0B',
              border: `1px solid ${isLiveApi ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
              fontWeight: '700'
            }}>
              {isLiveApi ? '● Live XAI Engine' : '○ Standby Diagnostics'}
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: 0 }}>
            <strong>What it does:</strong> Gives clear, human-readable explanations showing exactly *why* a call was marked as fake (e.g. sound pitch flat, low vocal variance, or zero natural breathing).
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setSelectedCase("elevenlabs")}
            style={{
              padding: '8px 16px', borderRadius: '8px', border: selectedCase === 'elevenlabs' ? '1px solid #EF4444' : '1px solid transparent',
              background: selectedCase === 'elevenlabs' ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.05)', color: selectedCase === 'elevenlabs' ? '#EF4444' : '#FFF', fontWeight: '700', cursor: 'pointer'
            }}
          >
            Explain Fake AI Voice
          </button>
          <button
            onClick={() => setSelectedCase("genuine")}
            style={{
              padding: '8px 16px', borderRadius: '8px', border: selectedCase === 'genuine' ? '1px solid #10B981' : '1px solid transparent',
              background: selectedCase === 'genuine' ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.05)', color: selectedCase === 'genuine' ? '#10B981' : '#FFF', fontWeight: '700', cursor: 'pointer'
            }}
          >
            Explain Real Voice
          </button>
        </div>
      </div>

      {/* Hero Image Banner */}
      <div className="image-banner-card" style={{ height: '220px', position: 'relative' }}>
        <img 
          src="/images/feature_xai.jpg" 
          onError={(e) => { e.currentTarget.src = "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=1200&q=80"; }} 
          alt="AI Acoustic Neural Signal & Explainability Engine" 
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(7, 9, 14, 0.1) 0%, rgba(7, 9, 14, 0.85) 100%)',
          display: 'flex', alignItems: 'flex-end', padding: '24px'
        }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: '800', color: '#3B82F6', textTransform: 'uppercase', letterSpacing: '1px' }}>
              🔍 Neural Forensic Diagnostic Engine
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: '#FFF', margin: '4px 0' }}>
              Deep Acoustic Feature Attribution & Biometric Audit Trail
            </h3>
            <p style={{ fontSize: '12px', color: '#D1D5DB', margin: 0 }}>
              Investigate pitch jitter, Mel-frequency spectral anomalies, phase distortion, and breathing lack in real-time.
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
        
        {/* Reasons List */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <Eye color="#06B6D4" size={20} /> Forensic Reason Breakdown
          </h3>
          <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Call ID: <strong style={{ color: '#06B6D4' }}>{curr.id}</strong></div>
          
          <div style={{ padding: '12px', borderRadius: '8px', background: curr.score >= 60 ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)', color: curr.score >= 60 ? '#EF4444' : '#10B981', fontWeight: '700', fontSize: '14px' }}>
            Result: {curr.verdict} (Risk Score: {curr.score} / 100)
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '6px' }}>
            {displayedReasons.map((r, idx) => (
              <div key={idx} style={{ padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: '3px solid #06B6D4', fontSize: '13px', lineHeight: '1.4' }}>
                {r}
              </div>
            ))}
          </div>
        </div>

        {/* Simplified Score Cards */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', margin: 0 }}>Tri-Layer Feature Contributions</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>SOUND QUALITY</div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: '#06B6D4' }}>{curr.breakdown.soundQuality}</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>SPEAKING STYLE</div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: '#F59E0B' }}>{curr.breakdown.speakingStyle}</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>VOICE MATCH</div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: '#EF4444' }}>{curr.breakdown.voiceMatch}</div>
            </div>
          </div>

          <div style={{ background: 'rgba(6,182,212,0.08)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(6,182,212,0.3)', marginTop: '10px' }}>
            <div style={{ fontWeight: '700', fontSize: '13px', color: '#06B6D4', marginBottom: '6px' }}>OFFICIAL SAFETY COMPLIANCE</div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4', margin: 0 }}>{curr.ruleCheck}</p>
          </div>

          <div style={{ padding: '14px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', fontSize: '12px', color: 'var(--text-muted)' }}>
            💡 <strong>Evidence Chain for Law Enforcement:</strong> Forensic attributes above can be exported directly as admissible technical evidence for cyber crime police investigations (CERT-In / I4C).
          </div>
        </div>

      </div>

    </div>
  );
}
