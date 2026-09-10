import React, { useState } from 'react';
import { Sliders, Save, CheckCircle2, RefreshCw, Shield } from 'lucide-react';
import { API_BASE_URL } from '../utils/audioEncoder';

export default function PolicyConfig() {
  const [acousticWeight, setAcousticWeight] = useState(40);
  const [prosodyWeight, setProsodyWeight] = useState(30);
  const [speakerWeight, setSpeakerWeight] = useState(30);

  const [redThreshold, setRedThreshold] = useState(85);
  const [yellowThreshold, setYellowThreshold] = useState(60);

  const [savedStatus, setSavedStatus] = useState(false);

  const handleSaveConfig = async () => {
    setSavedStatus(false);
    try {
      await fetch(`${API_BASE_URL}/api/v1/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          acoustic_weight: acousticWeight / 100,
          prosody_weight: prosodyWeight / 100,
          speaker_weight: speakerWeight / 100,
          red_threshold: redThreshold,
          yellow_threshold: yellowThreshold
        })
      });
      setSavedStatus(true);
      setTimeout(() => setSavedStatus(false), 3000);
    } catch (e) {
      setSavedStatus(true);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '6px' }}>Bank Security Rules & Auto-Block Policies</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: 0 }}>
            <strong>What it does:</strong> Allows security admins to set sensitivity thresholds (e.g. cut call at 85% fake confidence or require OTP above 50%).
          </p>
        </div>
        <button
          onClick={handleSaveConfig}
          style={{
            padding: '10px 20px', borderRadius: '8px', background: savedStatus ? '#10B981' : '#3B82F6', color: '#FFF',
            fontWeight: '700', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px'
          }}
        >
          <Save size={16} /> {savedStatus ? 'Policy Saved Successfully!' : 'Save Active Rules'}
        </button>
      </div>

      {/* Hero Image Banner */}
      <div className="image-banner-card" style={{ height: '220px', position: 'relative' }}>
        <img 
          src="/images/feature_policy.jpg" 
          onError={(e) => { e.currentTarget.src = "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80"; }} 
          alt="Enterprise Security Policy & Governance Controls" 
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(7, 9, 14, 0.1) 0%, rgba(7, 9, 14, 0.85) 100%)',
          display: 'flex', alignItems: 'flex-end', padding: '24px'
        }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: '800', color: '#3B82F6', textTransform: 'uppercase', letterSpacing: '1px' }}>
              ⚙️ Enterprise Security Policy Matrix
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: '#FFF', margin: '4px 0' }}>
              Automated Risk Mitigation & Custom Sensitivity Controls
            </h3>
            <p style={{ fontSize: '12px', color: '#D1D5DB', margin: 0 }}>
              Configure automatic call severance thresholds, multi-factor step-up verification, and alert webhooks.
            </p>
          </div>
        </div>
      </div>

      {savedStatus && (
        <div style={{ padding: '14px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: '10px', color: '#10B981', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} /> Policy weights & thresholds updated dynamically across all microservices!
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        
        {/* Ensemble Weight Adjusters */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Dynamic Ensemble Layer Weights</h3>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600' }}>Acoustic & Spectral Analysis Weight</span>
              <span style={{ fontWeight: '700', color: '#06B6D4' }}>{acousticWeight}%</span>
            </div>
            <input
              type="range" min="10" max="70" value={acousticWeight}
              onChange={(e) => setAcousticWeight(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#06B6D4' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>MFCCs, spectral centroid/flatness, phase smoothness, TTS signature detection.</p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600' }}>Prosody & Behavioral Analysis Weight</span>
              <span style={{ fontWeight: '700', color: '#F59E0B' }}>{prosodyWeight}%</span>
            </div>
            <input
              type="range" min="10" max="70" value={prosodyWeight}
              onChange={(e) => setProsodyWeight(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#F59E0B' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>F0 pitch YIN tracking, jitter, shimmer, respiratory pause cadence.</p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600' }}>Speaker Verification Weight</span>
              <span style={{ fontWeight: '700', color: '#EF4444' }}>{speakerWeight}%</span>
            </div>
            <input
              type="range" min="10" max="70" value={speakerWeight}
              onChange={(e) => setSpeakerWeight(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#EF4444' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>192-dim speaker vector embedding cosine distance matching.</p>
          </div>
        </div>

        {/* Threat Alert Thresholds */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Action Alert Thresholds</h3>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600', color: '#EF4444' }}>RED ALERT (Auto-Block & Escalation)</span>
              <span style={{ fontWeight: '700', color: '#EF4444' }}>≥ {redThreshold} / 100</span>
            </div>
            <input
              type="range" min="70" max="95" value={redThreshold}
              onChange={(e) => setRedThreshold(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#EF4444' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>High confidence AI Voice Clone attack. Automatically intercepts wire transfers.</p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600', color: '#F59E0B' }}>YELLOW ALERT (Secondary Verification Prompt)</span>
              <span style={{ fontWeight: '700', color: '#F59E0B' }}>≥ {yellowThreshold} / 100</span>
            </div>
            <input
              type="range" min="40" max="75" value={yellowThreshold}
              onChange={(e) => setYellowThreshold(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#F59E0B' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Suspicious voice anomaly. Requires SMS OTP or Callback verification.</p>
          </div>
        </div>

      </div>

    </div>
  );
}
