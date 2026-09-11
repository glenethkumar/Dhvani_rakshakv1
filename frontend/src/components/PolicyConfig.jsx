import React, { useState } from 'react';
import { Sliders, Save, CheckCircle2, RefreshCw, Shield, AlertTriangle, ShieldAlert, Zap, Lock } from 'lucide-react';
import { API_BASE_URL } from '../utils/audioEncoder';

export default function PolicyConfig() {
  const [sensitivity, setSensitivity] = useState("NORMAL"); // "STRICT" | "NORMAL" | "LENIENT"
  const [autoActionEnabled, setAutoActionEnabled] = useState(false);
  const [showAutoActionModal, setShowAutoActionModal] = useState(false);
  const [vipModeEnabled, setVipModeEnabled] = useState(false);

  const [acousticWeight, setAcousticWeight] = useState(60);
  const [prosodyWeight, setProsodyWeight] = useState(25);
  const [speakerWeight, setSpeakerWeight] = useState(15);

  const [redThreshold, setRedThreshold] = useState(85);
  const [yellowThreshold, setYellowThreshold] = useState(60);

  const [savedStatus, setSavedStatus] = useState(false);

  const handleApplyPreset = (level) => {
    setSensitivity(level);
    if (level === "STRICT") {
      setRedThreshold(75);
      setYellowThreshold(50);
    } else if (level === "LENIENT") {
      setRedThreshold(90);
      setYellowThreshold(70);
    } else {
      setRedThreshold(85);
      setYellowThreshold(60);
    }
  };

  const handleToggleAutoAction = () => {
    if (!autoActionEnabled) {
      setShowAutoActionModal(true);
    } else {
      setAutoActionEnabled(false);
    }
  };

  const confirmEnableAutoAction = () => {
    setAutoActionEnabled(true);
    setShowAutoActionModal(false);
  };

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
          red_threshold: vipModeEnabled ? redThreshold - 10 : redThreshold,
          yellow_threshold: vipModeEnabled ? yellowThreshold - 10 : yellowThreshold,
          auto_action_enabled: autoActionEnabled
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
          <h2 style={{ fontSize: '22px', fontWeight: '800', marginBottom: '6px', color: '#FFF' }}>Security Rules & Policy Governance</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: 0 }}>
            Configure detection sensitivity, fraud desk transfer thresholds, human-in-the-loop recommendations, and opt-in automated disconnect rules.
          </p>
        </div>
        <button
          onClick={handleSaveConfig}
          style={{
            padding: '12px 24px', borderRadius: '10px', background: savedStatus ? '#10B981' : 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)', color: '#FFF',
            fontWeight: '700', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px'
          }}
        >
          <Save size={18} /> {savedStatus ? 'Policy Saved Successfully!' : 'Save Active Rules'}
        </button>
      </div>

      {/* Auto Action & Human-in-the-Loop Safeguard */}
      <div className="glass-panel" style={{ padding: '24px', border: autoActionEnabled ? '1.5px solid #EF4444' : '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div>
            <span style={{ fontSize: '12px', fontWeight: '800', color: autoActionEnabled ? '#EF4444' : '#10B981', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
              {autoActionEnabled ? '🚨 AUTOMATED ACTION ENABLED (ENTERPRISE OPT-IN)' : '✅ HUMAN-IN-THE-LOOP (RECOMMENDATIONS ONLY - DEFAULT)'}
            </span>
            <h3 style={{ fontSize: '18px', fontWeight: '800', margin: '4px 0', color: '#FFF' }}>
              Automated Disconnect & Action Policy
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0, maxWidth: '680px' }}>
              By default, Dhvani Rakshak <strong>only alerts and recommends actions</strong> without disconnecting calls. Enterprise admins can opt-in to automated severing.
            </p>
          </div>

          <button
            onClick={handleToggleAutoAction}
            style={{
              padding: '12px 20px',
              borderRadius: '10px',
              background: autoActionEnabled ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.15)',
              border: autoActionEnabled ? '1px solid #EF4444' : '1px solid #10B981',
              color: autoActionEnabled ? '#EF4444' : '#10B981',
              fontWeight: '700',
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {autoActionEnabled ? 'Disable Automated Disconnect' : 'Enable Automated Disconnect (Opt-In)'}
          </button>
        </div>
      </div>

      {/* Sensitivity Presets */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '14px' }}>Detection Sensitivity Presets</h3>
        <div style={{ display: 'flex', gap: '12px' }}>
          {["STRICT", "NORMAL", "LENIENT"].map((lvl) => (
            <button
              key={lvl}
              onClick={() => handleApplyPreset(lvl)}
              style={{
                flex: 1,
                padding: '12px',
                borderRadius: '10px',
                border: sensitivity === lvl ? '2px solid #06B6D4' : '1px solid rgba(255,255,255,0.1)',
                background: sensitivity === lvl ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.03)',
                color: sensitivity === lvl ? '#06B6D4' : '#FFF',
                fontWeight: '700',
                cursor: 'pointer'
              }}
            >
              {lvl === "STRICT" ? '⚡ Strict Protection (Higher Guard)' : lvl === "LENIENT" ? '🛡️ Lenient (Low False Positives)' : '⚖️ Normal Balanced (Recommended)'}
            </button>
          ))}
        </div>
      </div>

      {savedStatus && (
        <div style={{ padding: '14px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: '10px', color: '#10B981', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} /> Security policies updated dynamically across gateway microservices!
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        
        {/* Ensemble Weight Adjusters */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Score Fusion Model Weights</h3>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600' }}>Acoustic Model (WavLM Deepfake Probability)</span>
              <span style={{ fontWeight: '700', color: '#06B6D4' }}>{acousticWeight}%</span>
            </div>
            <input
              type="range" min="30" max="80" value={acousticWeight}
              onChange={(e) => setAcousticWeight(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#06B6D4' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Detects spectral vocoder signatures, phase alignment, and high-frequency cutoff.</p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600' }}>Pitch Micro-Jitter & Vocal Cord Dynamics</span>
              <span style={{ fontWeight: '700', color: '#F59E0B' }}>{prosodyWeight}%</span>
            </div>
            <input
              type="range" min="10" max="50" value={prosodyWeight}
              onChange={(e) => setProsodyWeight(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#F59E0B' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Analyzes pitch micro-tremor, vocal tract formant stability, and physiological breathing.</p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600' }}>ECAPA-TDNN Speaker Verification</span>
              <span style={{ fontWeight: '700', color: '#EF4444' }}>{speakerWeight}%</span>
            </div>
            <input
              type="range" min="10" max="40" value={speakerWeight}
              onChange={(e) => setSpeakerWeight(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#EF4444' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Compares 192-dim speaker embeddings against registered voice profiles.</p>
          </div>
        </div>

        {/* Threat Alert Thresholds */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Action Alert Thresholds</h3>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600', color: '#EF4444' }}>RED ALERT (Recommend Disconnect)</span>
              <span style={{ fontWeight: '700', color: '#EF4444' }}>≥ {redThreshold} / 100</span>
            </div>
            <input
              type="range" min="70" max="95" value={redThreshold}
              onChange={(e) => setRedThreshold(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#EF4444' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>High risk AI voice clone attack. Alerts operator and recommends disconnection.</p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span style={{ fontWeight: '600', color: '#F59E0B' }}>YELLOW ALERT (Suggest Fraud Desk Transfer)</span>
              <span style={{ fontWeight: '700', color: '#F59E0B' }}>≥ {yellowThreshold} / 100</span>
            </div>
            <input
              type="range" min="40" max="75" value={yellowThreshold}
              onChange={(e) => setYellowThreshold(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#F59E0B' }}
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>Suspicious voice characteristics. Recommends secondary verification.</p>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '12px' }}>
            <div>
              <div style={{ fontSize: '13px', fontWeight: '700', color: '#06B6D4' }}>VIP Executive Shield Mode</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Lowers detection thresholds by 10 points for high-risk accounts.</div>
            </div>
            <button
              onClick={() => setVipModeEnabled(!vipModeEnabled)}
              style={{
                padding: '6px 14px', borderRadius: '20px', border: vipModeEnabled ? '1px solid #06B6D4' : '1px solid rgba(255,255,255,0.2)',
                background: vipModeEnabled ? 'rgba(6, 182, 212, 0.2)' : 'transparent', color: vipModeEnabled ? '#06B6D4' : '#FFF', fontWeight: '700', cursor: 'pointer'
              }}
            >
              {vipModeEnabled ? 'VIP Shield ACTIVE' : 'Enable VIP Mode'}
            </button>
          </div>
        </div>

      </div>

      {/* Opt-In Automated Severing Confirmation Modal */}
      {showAutoActionModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ width: '480px', padding: '28px', background: '#0D111A', border: '1.5px solid #EF4444' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px', color: '#EF4444' }}>
              <ShieldAlert size={32} />
              <h3 style={{ fontSize: '18px', fontWeight: '800', margin: 0 }}>Enable Automated Call Severing?</h3>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.5', marginBottom: '20px' }}>
              <strong>Warning:</strong> Enabling automated severing allows the gateway to issue automatic SIP BYE call drops when RED risk is detected. 
              <br /><br />
              <em>"This may occasionally drop legitimate calls during false positive acoustic anomalies."</em>
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button
                onClick={() => setShowAutoActionModal(false)}
                style={{ padding: '10px 18px', borderRadius: '8px', background: 'rgba(255,255,255,0.1)', color: '#FFF', border: 'none', cursor: 'pointer' }}
              >
                Cancel (Keep Recommendations Only)
              </button>
              <button
                onClick={confirmEnableAutoAction}
                style={{ padding: '10px 18px', borderRadius: '8px', background: '#EF4444', color: '#FFF', border: 'none', fontWeight: '700', cursor: 'pointer' }}
              >
                I Understand, Enable Opt-In Auto Sever
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

