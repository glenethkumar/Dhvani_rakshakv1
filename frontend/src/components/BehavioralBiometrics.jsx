import React, { useState } from 'react';
import { Activity, MousePointer, Clock, ShieldAlert } from 'lucide-react';

export default function BehavioralBiometrics() {
  const [typingCps, setTypingCps] = useState(4.2);
  const [mouseJitter, setMouseJitter] = useState(0.15);
  const [emotionalState, setEmotionalState] = useState("HIGH_STRESS_URGENT");
  const [isGeoAnomaly, setIsGeoAnomaly] = useState(true);

  const isBotTyping = typingCps > 11.0 || typingCps < 0.5;
  const isOffHours = true;
  
  const behavioralRisk = (
    (isBotTyping ? 35 : 5) +
    (isOffHours ? 30 : 5) +
    (isGeoAnomaly ? 25 : 5) +
    (emotionalState === "HIGH_STRESS_URGENT" ? 10 : 2)
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '6px' }}>User Behavior Check</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: 0 }}>
            <strong>What it does:</strong> Checks caller emotional stress levels, unusual midnight call times, and computer/mouse behavior to detect scam urgency and automated bot scripts.
          </p>
        </div>
        <div style={{ padding: '8px 16px', borderRadius: '20px', background: behavioralRisk > 60 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)', color: behavioralRisk > 60 ? '#EF4444' : '#10B981', border: '1px solid', borderColor: behavioralRisk > 60 ? '#EF4444' : '#10B981', fontSize: '13px', fontWeight: '700' }}>
          BEHAVIOR RISK: {behavioralRisk} / 100
        </div>
      </div>

      {/* Hero Image Banner */}
      <div className="image-banner-card" style={{ height: '220px', position: 'relative' }}>
        <img 
          src="/images/feature_behavioral.jpg" 
          onError={(e) => { e.currentTarget.src = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80"; }} 
          alt="Behavioral Biometrics Analytics & Keystroke Dynamics" 
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(7, 9, 14, 0.1) 0%, rgba(7, 9, 14, 0.85) 100%)',
          display: 'flex', alignItems: 'flex-end', padding: '24px'
        }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: '800', color: '#F59E0B', textTransform: 'uppercase', letterSpacing: '1px' }}>
              🧠 Cognitive & Neuromotor Profiling
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: '#FFF', margin: '4px 0' }}>
              Continuous Behavioral Biometrics & Contextual Risk Engine
            </h3>
            <p style={{ fontSize: '12px', color: '#D1D5DB', margin: 0 }}>
              Real-time monitoring of keystroke flight time, cursor micro-tremors, and voice stress pressure.
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>TYPING SPEED</div>
          <div style={{ fontSize: '22px', fontWeight: '800', color: isBotTyping ? '#EF4444' : '#10B981' }}>{typingCps} Chars/Sec</div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
            {isBotTyping ? 'Automatic Script Bot' : 'Normal Human Typing'}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>MOUSE MOVEMENTS</div>
          <div style={{ fontSize: '22px', fontWeight: '800', color: mouseJitter < 0.05 ? '#EF4444' : '#06B6D4' }}>
            {mouseJitter < 0.05 ? 'Bot Straight Line' : 'Human Natural Curve'}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Movement Score: {mouseJitter}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>EMOTIONAL URGENCY</div>
          <div style={{ fontSize: '18px', fontWeight: '800', color: emotionalState.includes('STRESS') ? '#F59E0B' : '#10B981' }}>
            {emotionalState.replace('_', ' ')}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Voice Pressure Tactics
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>NETWORK & TIME</div>
          <div style={{ fontSize: '18px', fontWeight: '800', color: isGeoAnomaly ? '#EF4444' : '#10B981' }}>
            {isGeoAnomaly ? 'VPN / Unknown IP' : 'Trusted IP'}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Calling Time: 03:15 AM (Off-hours)
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Test User Behavior Simulation</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
              Simulated Typing Speed: {typingCps} Chars/Sec
            </label>
            <input
              type="range" min="1" max="18" step="0.5" value={typingCps}
              onChange={(e) => setTypingCps(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#06B6D4' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
              Simulated Emotional Tone
            </label>
            <select
              value={emotionalState} onChange={(e) => setEmotionalState(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '8px', background: '#0A0D14', color: '#FFF', border: '1px solid rgba(255,255,255,0.15)' }}
            >
              <option value="HIGH_STRESS_URGENT">High Stress / Urgent Tactics</option>
              <option value="PANICKED">Panicked / Aggressive Pressure</option>
              <option value="CALM_NEUTRAL">Calm / Normal Tone</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
