import React, { useState } from 'react';
import { ShieldAlert, Radio, Award, CheckCircle, RefreshCw, Send, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '../utils/audioEncoder';

export default function GovVipProtection() {
  const [dignitaries] = useState([
    { id: "GOV_001", name: "Shri Amit Varma (IAS - Principal Secretary)", agency: "Ministry of Home Affairs", tier: "ULTRA HIGH SECURITY", status: "PROTECTED" },
    { id: "GOV_002", name: "IPS R. K. Singh (Director General)", agency: "National Security Guard", tier: "COMMANDO DISPATCH", status: "PROTECTED" },
    { id: "GOV_003", name: "Dr. S. Jaishankar (Dignitary Desk)", agency: "Ministry of External Affairs", tier: "HIGH SECURITY", status: "PROTECTED" }
  ]);

  const [activeDispatch, setActiveDispatch] = useState(null);
  const [callingApi, setCallingApi] = useState(false);
  const [isLiveApi, setIsLiveApi] = useState(false);

  const handleSimulateGovAttack = async () => {
    setCallingApi(true);
    try {
      const formData = new FormData();
      formData.append("caller_id", "+91 98111 88200");
      formData.append("risk_score", "94.5");

      const res = await fetch(`${API_BASE_URL}/api/v1/gov-protect`, {
        method: "POST",
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        setIsLiveApi(true);
        setActiveDispatch({
          incidentId: data.incident_id || `INCIDENT_GOV_${Math.floor(100 + Math.random() * 900)}`,
          dignitary: data.dignitary || "Shri Amit Varma (IAS - Principal Secretary)",
          agency: data.agency || "Ministry of Home Affairs",
          action: data.action || "CALL IMMEDIATELY CUT & POLICE DISPATCHED",
          dispatchTargets: data.dispatch_targets || ["CRPF Cyber Incident Response Team", "Ministry Command Desk", "National Security Team", "I4C Cybercrime Unit"],
          timestamp: new Date().toISOString()
        });
      } else {
        throw new Error();
      }
    } catch (err) {
      setIsLiveApi(false);
      setActiveDispatch({
        incidentId: `INCIDENT_GOV_${Math.floor(100 + Math.random() * 900)}`,
        dignitary: "Shri Amit Varma (IAS - Principal Secretary)",
        agency: "Ministry of Home Affairs",
        action: "CALL IMMEDIATELY CUT & POLICE DISPATCHED (STANDBY)",
        dispatchTargets: ["CRPF Cyber Incident Response Team", "Ministry Command Desk", "National Security Team"],
        timestamp: new Date().toISOString()
      });
    } finally {
      setCallingApi(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Header Card */}
      <div className="glass-panel glow-red" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '4px solid #EF4444', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <h2 style={{ fontSize: '22px', fontWeight: '700', margin: 0, color: '#EF4444', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Award size={24} /> VIP & Government Official Protection Shield
            </h2>
            <span style={{
              fontSize: '11px', padding: '3px 10px', borderRadius: '20px',
              background: isLiveApi ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              color: isLiveApi ? '#10B981' : '#F59E0B',
              border: `1px solid ${isLiveApi ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
              fontWeight: '700'
            }}>
              {isLiveApi ? '● Live Dispatch Webhook' : '○ Standby Shield'}
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: 0 }}>
            <strong>What it does:</strong> Ultra-high security shield for IAS/IPS officers, military leaders, and bank executives. If an AI voice imposter calls, it cuts the call and triggers instant emergency police dispatch.
          </p>
        </div>

        <button
          onClick={handleSimulateGovAttack}
          disabled={callingApi}
          style={{
            padding: '12px 22px', borderRadius: '10px', background: '#EF4444', color: '#FFF',
            fontWeight: '700', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
            boxShadow: '0 0 15px rgba(239, 68, 68, 0.4)'
          }}
        >
          {callingApi ? <RefreshCw size={16} className="animate-spin" /> : <Send size={16} />}
          {callingApi ? 'Triggering Dispatch...' : 'Simulate VIP Threat Attack'}
        </button>
      </div>

      {/* Visual VIP Defense Badge Graphic */}
      <div className="image-banner-card" style={{ height: '230px', position: 'relative' }}>
        <img 
          src="/images/feature_gov.jpg" 
          onError={(e) => { e.currentTarget.src = "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1200&q=80"; }} 
          alt="Government Security Headquarters Defense" 
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(7, 9, 14, 0.1) 0%, rgba(7, 9, 14, 0.85) 100%)',
          display: 'flex', alignItems: 'flex-end', padding: '24px'
        }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: '800', color: '#EF4444', textTransform: 'uppercase', letterSpacing: '1px' }}>
              🎖️ Official National Security Protocol
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: '#FFF', margin: '4px 0' }}>
              Government Defense & IAS / IPS Officer Priority Shield
            </h3>
            <p style={{ fontSize: '12px', color: '#D1D5DB', margin: 0 }}>
              Integrated with emergency agency feeds, automated incident logging, and zero-trust secondary biometric challenge protocols.
            </p>
          </div>
        </div>
      </div>

      {/* Live Dispatch Active Card */}
      {activeDispatch && (
        <div className="glass-panel" style={{ padding: '24px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #EF4444', animation: 'fadeIn 0.3s ease' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#EF4444', fontWeight: '800', fontSize: '16px', marginBottom: '10px' }}>
            <ShieldAlert size={24} /> FAKE VOICE DETECTED ON VIP LINE - EMERGENCY DISPATCH ACTIVE
          </div>
          <div style={{ fontSize: '13px', color: '#F3F4F6', marginBottom: '12px' }}>
            Target Official: <strong>{activeDispatch.dignitary}</strong> ({activeDispatch.agency}) • Incident ID: <span style={{ fontFamily: 'monospace', color: '#06B6D4' }}>{activeDispatch.incidentId}</span>
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {activeDispatch.dispatchTargets.map((t, idx) => (
              <span key={idx} style={{ padding: '6px 12px', background: '#0D111A', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.2)', fontSize: '12px', color: '#06B6D4', fontWeight: '600' }}>
                ✓ Alert Sent: {t}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Protected Dignitary Roster Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>Protected Government Profiles</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px' }}>OFFICIAL ID</th>
                <th style={{ padding: '10px' }}>NAME & POSITION</th>
                <th style={{ padding: '10px' }}>MINISTRY / AGENCY</th>
                <th style={{ padding: '10px' }}>SECURITY TIER</th>
                <th style={{ padding: '10px' }}>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {dignitaries.map((d) => (
                <tr key={d.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 10px', fontFamily: 'monospace', color: '#06B6D4' }}>{d.id}</td>
                  <td style={{ padding: '12px 10px', fontWeight: '700', color: '#FFF' }}>{d.name}</td>
                  <td style={{ padding: '12px 10px', color: 'var(--text-muted)' }}>{d.agency}</td>
                  <td style={{ padding: '12px 10px' }}>
                    <span style={{ fontSize: '10px', fontWeight: '800', padding: '3px 8px', borderRadius: '6px', background: 'rgba(239,68,68,0.2)', color: '#EF4444' }}>
                      {d.tier}
                    </span>
                  </td>
                  <td style={{ padding: '12px 10px', color: '#10B981', fontWeight: '700' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <CheckCircle size={14} /> {d.status}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
