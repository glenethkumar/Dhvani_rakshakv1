import React, { useState, useEffect } from 'react';
import {
  PhoneCall, PhoneIncoming, PhoneOff, Shield, ShieldCheck, ShieldAlert,
  Server, Cpu, Activity, AlertTriangle, RefreshCw, Radio, UserCheck,
  ArrowRight, PhoneForwarded, Volume2, Key, CheckCircle2, Lock
} from 'lucide-react';
import { API_BASE_URL } from '../utils/audioEncoder';

export default function TelecomGateway() {
  const [trunkStatus, setTrunkStatus] = useState({
    trunk_name: "Enterprise PBX Trunk Gateway (Asterisk / FreeSWITCH / Twilio SIP)",
    trunk_status: "CONNECTED",
    active_call_count: 3,
    total_calls_monitored: 42,
    supported_codecs: ["PCMU (G.711u)", "PCMA (G.711a)", "PCM16", "G.722"],
    auto_action_policy_enabled: false,
    recommended_actions_enabled: true
  });

  const [activeCalls, setActiveCalls] = useState([
    {
      call_sid: "CA_9B18F203AA01",
      caller_number: "+91 98200 12345",
      dialed_number: "+91 22 6600 0000",
      carrier: "PBX Trunk Line",
      codec: "PCMU (G.711u)",
      status: "IN_PROGRESS",
      duration_sec: 48.2,
      cumulative_risk: 18.4,
      alert_level: "GREEN",
      detected_vocoder: "None",
      trai_dlt: { status: "DLT Verified — Full KYC", level: "FULL_KYC", is_spoofed: false }
    },
    {
      call_sid: "CA_4E72B109DC88",
      caller_number: "+91 98111 54321",
      dialed_number: "+91 22 6600 0000",
      carrier: "SIP Trunk",
      codec: "PCMA (G.711a)",
      status: "SUGGEST_FRAUD_DESK_TRANSFER",
      duration_sec: 62.5,
      cumulative_risk: 74.5,
      alert_level: "YELLOW",
      detected_vocoder: "OpenAI_Voice",
      trai_dlt: { status: "DLT Verified — Partial", level: "PARTIAL", is_spoofed: false }
    },
    {
      call_sid: "CA_1A88C490EF22",
      caller_number: "+91 00000 00000",
      dialed_number: "+91 22 6600 0000",
      carrier: "Generic VoIP",
      codec: "PCMU (G.711u)",
      status: "RECOMMEND_DISCONNECT",
      duration_sec: 14.1,
      cumulative_risk: 94.8,
      alert_level: "RED",
      detected_vocoder: "ElevenLabs",
      trai_dlt: { status: "Unverified / Spoofed", level: "UNVERIFIED", is_spoofed: true }
    }
  ]);

  // Dialer simulation state
  const [scenario, setScenario] = useState("elevenlabs_clone");
  const [callerNumber, setCallerNumber] = useState("+91 98200 12345");
  const [carrier, setCarrier] = useState("Airtel");
  const [codec, setCodec] = useState("PCMU");
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);

  const fetchTrunkData = async () => {
    try {
      const [resTrunk, resCalls] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/telecom/trunk-status`),
        fetch(`${API_BASE_URL}/api/v1/telecom/active-calls`)
      ]);
      if (resTrunk.ok) {
        const data = await resTrunk.json();
        setTrunkStatus(data);
      }
      if (resCalls.ok) {
        const callsData = await resCalls.json();
        if (callsData.active_calls && callsData.active_calls.length > 0) {
          setActiveCalls(callsData.active_calls);
        }
      }
    } catch (e) {
      console.warn("Telemetry fetch note:", e);
    }
  };

  useEffect(() => {
    fetchTrunkData();
    const interval = setInterval(fetchTrunkData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSimulateCall = async () => {
    setSimulating(true);
    setSimulationResult(null);
    setActionMessage(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/telecom/simulate-call`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario,
          carrier,
          caller_number: callerNumber,
          codec,
          target_speaker: "VIP_CEO"
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSimulationResult(data);
        fetchTrunkData();
      } else {
        alert("Telecom simulation request failed. Ensure backend server is running.");
      }
    } catch (err) {
      alert("Error contacting telecom gateway: " + err.message);
    } finally {
      setSimulating(false);
    }
  };

  const handleExecuteAction = async (callSid, action) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/telecom/call-action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          call_sid: callSid,
          action,
          notes: `Operator action triggered: ${action}`
        })
      });
      if (res.ok) {
        const data = await res.json();
        setActionMessage({ sid: callSid, message: data.message });
        fetchTrunkData();
        setTimeout(() => setActionMessage(null), 6000);
      }
    } catch (e) {
      alert("Action execution failed: " + e.message);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#06B6D4' }}>
              <Radio size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '22px', fontWeight: '700', margin: 0 }}>Enterprise Telecom & PBX Gateway</h2>
              <span style={{ fontSize: '12px', color: '#10B981', fontWeight: '700' }}>
                ● {trunkStatus.trunk_name} ({trunkStatus.trunk_status})
              </span>
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: '6px 0 0 0' }}>
            <strong>What it does:</strong> Directly intercepts live telephone voice streams from enterprise PBX trunks (Asterisk, FreeSWITCH, Twilio SIP), decodes G.711 $\mu$-law/A-law audio, verifies STIR/SHAKEN caller signatures, and drops AI voice clones via automated <strong>SIP BYE</strong> disconnect.
          </p>
        </div>

        <button
          onClick={fetchTrunkData}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '10px 18px', background: 'rgba(6, 182, 212, 0.15)', border: '1px solid #06B6D4',
            borderRadius: '10px', color: '#06B6D4', fontWeight: '700', cursor: 'pointer'
          }}
        >
          <RefreshCw size={16} />
          Refresh Trunk Status
        </button>
      </div>

      {/* Trunk Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700' }}>SIP TRUNK LINE HEALTH</span>
            <Server size={18} color="#06B6D4" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#10B981', marginBottom: '4px' }}>100% OPERATIONAL</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Asterisk AudioSocket / Twilio Stream</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700' }}>AUTOMATED SIP DEFENSE</span>
            <PhoneOff size={18} color="#EF4444" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#EF4444', marginBottom: '4px' }}>SIP BYE (Code 603)</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Auto-Sever Call on RED Risk (Score &ge; 85)</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700' }}>FRAUD DESK DEFLECTION</span>
            <PhoneForwarded size={18} color="#F59E0B" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#F59E0B', marginBottom: '4px' }}>SIP REFER Transfer</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Auto-Reroute to Fraud Desk on YELLOW (Score &ge; 60)</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '700' }}>TELECOM CODECS DECODED</span>
            <Cpu size={18} color="#8B5CF6" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#8B5CF6', marginBottom: '4px' }}>G.711u / G.711a</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>8kHz &rarr; 16kHz Polyphase Resampling</div>
        </div>

      </div>

      {/* Interactive Telecom Inbound Call Simulator */}
      <div className="glass-panel" style={{ padding: '24px', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <PhoneIncoming size={20} color="#06B6D4" />
          Interactive Inbound Telephony Stream Simulator
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
          Simulate an inbound phone call arriving through the telecom network. Audio is encoded into G.711 $\mu$-law bytes with PSTN line degradation, fed into the AASIST neural engine, and evaluated for automated mid-call mitigation.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '6px' }}>
              SIMULATED CALL SCENARIO:
            </label>
            <select
              value={scenario}
              onChange={(e) => {
                setScenario(e.target.value);
                if (e.target.value === "elevenlabs_clone") {
                  setCallerNumber("+91 00000 00000");
                  setCarrier("Generic_VoIP");
                } else if (e.target.value === "genuine_ceo") {
                  setCallerNumber("+91 98200 12345");
                  setCarrier("Airtel");
                } else {
                  setCallerNumber("+91 98765 43210");
                  setCarrier("Reliance Jio");
                }
              }}
              style={{ width: '100%', padding: '10px 12px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '8px', color: 'white', fontWeight: '600' }}
            >
              <option value="elevenlabs_clone" style={{ background: '#0F172A' }}>ElevenLabs AI Voice Clone (Spoofed VIP)</option>
              <option value="genuine_ceo" style={{ background: '#0F172A' }}>Authentic CEO Wire Call (Bona Fide Human)</option>
              <option value="spliced_attack" style={{ background: '#0F172A' }}>Spliced Voice Cut Attack (Mid-Call Edit)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '6px' }}>
              CALLER ANI / PHONE NUMBER:
            </label>
            <input
              type="text"
              value={callerNumber}
              onChange={(e) => setCallerNumber(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '8px', color: 'white', fontWeight: '600' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '6px' }}>
              ORIGINATING TELECOM CARRIER:
            </label>
            <select
              value={carrier}
              onChange={(e) => setCarrier(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '8px', color: 'white', fontWeight: '600' }}
            >
              <option value="Airtel" style={{ background: '#0F172A' }}>Bharti Airtel (Direct PSTN)</option>
              <option value="Reliance Jio" style={{ background: '#0F172A' }}>Reliance Jio (VoLTE)</option>
              <option value="Vodafone Idea" style={{ background: '#0F172A' }}>Vodafone Idea (Vi)</option>
              <option value="Generic_VoIP" style={{ background: '#0F172A' }}>Generic_VoIP (Untrusted Gateway - Spoofed)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '6px' }}>
              TELECOM CODEC:
            </label>
            <select
              value={codec}
              onChange={(e) => setCodec(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '8px', color: 'white', fontWeight: '600' }}
            >
              <option value="PCMU" style={{ background: '#0F172A' }}>G.711 &mu;-law (8kHz PCMU)</option>
              <option value="PCMA" style={{ background: '#0F172A' }}>G.711 A-law (8kHz PCMA)</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSimulateCall}
          disabled={simulating}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '12px 24px', background: 'linear-gradient(135deg, #06B6D4 0%, #0284C7 100%)',
            border: 'none', borderRadius: '10px', color: 'white', fontWeight: '700',
            cursor: 'pointer', fontSize: '14px'
          }}
        >
          <PhoneCall size={18} className={simulating ? 'animate-spin' : ''} />
          {simulating ? 'Processing Telephony Stream...' : 'Dial Inbound Telecom Call (Simulate)'}
        </button>

        {/* Live Simulation Result Display */}
        {simulationResult && (
          <div style={{ marginTop: '24px', padding: '20px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>CALL SID:</span>
                <span style={{ fontWeight: '800', marginLeft: '8px', color: '#06B6D4' }}>{simulationResult.session.call_sid}</span>
                <span style={{ marginLeft: '16px', fontSize: '12px', color: 'var(--text-muted)' }}>CARRIER: {simulationResult.session.carrier}</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{
                  fontSize: '11px', padding: '4px 10px', borderRadius: '20px',
                  background: simulationResult.session.stir_shaken?.attestation_level === 'A' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                  color: simulationResult.session.stir_shaken?.attestation_level === 'A' ? '#10B981' : '#EF4444',
                  fontWeight: '700', border: '1px solid currentColor'
                }}>
                  STIR/SHAKEN Attestation: Level {simulationResult.session.stir_shaken?.attestation_level || 'A'}
                </span>
                {simulationResult.session.stir_shaken?.is_cli_spoofed && (
                  <span style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '20px', background: 'rgba(239,68,68,0.2)', color: '#EF4444', fontWeight: '700' }}>
                    CLI SPOOFING FLAGGED
                  </span>
                )}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '16px' }}>
              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(255,255,255,0.03)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>RISK SCORE</div>
                <div style={{
                  fontSize: '22px', fontWeight: '800',
                  color: simulationResult.chunk_evaluation.alert_level === 'RED' ? '#EF4444' : simulationResult.chunk_evaluation.alert_level === 'YELLOW' ? '#F59E0B' : '#10B981'
                }}>
                  {simulationResult.chunk_evaluation.risk_score} / 100 ({simulationResult.chunk_evaluation.alert_level})
                </div>
              </div>

              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(255,255,255,0.03)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>NEURAL VOCODER PROBABILITY</div>
                <div style={{ fontSize: '22px', fontWeight: '800', color: '#06B6D4' }}>
                  {(simulationResult.chunk_evaluation.neural_deepfake_prob * 100).toFixed(1)}%
                </div>
              </div>

              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(255,255,255,0.03)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>SPEAKER IDENTITY MATCH</div>
                <div style={{ fontSize: '22px', fontWeight: '800', color: simulationResult.chunk_evaluation.speaker_similarity > 0.8 ? '#10B981' : '#EF4444' }}>
                  {(simulationResult.chunk_evaluation.speaker_similarity * 100).toFixed(1)}%
                </div>
              </div>

              <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(255,255,255,0.03)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>DEFENSE ACTION TRIGGERED</div>
                <div style={{ fontSize: '16px', fontWeight: '800', color: simulationResult.chunk_evaluation.mitigation_action === 'TERMINATED_BY_SIP_BYE' ? '#EF4444' : simulationResult.chunk_evaluation.mitigation_action === 'DEFLECTED_TO_FRAUD_DESK' ? '#F59E0B' : '#10B981' }}>
                  {simulationResult.chunk_evaluation.mitigation_action}
                </div>
              </div>
            </div>

            {/* SIP Action Command Card */}
            {simulationResult.chunk_evaluation.sip_command && (
              <div style={{
                padding: '14px 18px', borderRadius: '10px',
                background: simulationResult.chunk_evaluation.sip_command.action === 'SEND_SIP_BYE' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                border: `1px solid ${simulationResult.chunk_evaluation.sip_command.action === 'SEND_SIP_BYE' ? '#EF4444' : '#F59E0B'}`,
                display: 'flex', alignItems: 'center', gap: '14px'
              }}>
                <ShieldAlert size={24} color={simulationResult.chunk_evaluation.sip_command.action === 'SEND_SIP_BYE' ? '#EF4444' : '#F59E0B'} />
                <div>
                  <div style={{ fontWeight: '800', fontSize: '14px' }}>
                    PBX Automated Defense Command: {simulationResult.chunk_evaluation.sip_command.action}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {simulationResult.chunk_evaluation.sip_command.action === 'SEND_SIP_BYE' 
                      ? `SIP Code 603: ${simulationResult.chunk_evaluation.sip_command.sip_reason}`
                      : `SIP REFER: Transferred to Fraud Specialist Desk (${simulationResult.chunk_evaluation.sip_command.transfer_number})`}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Active Monitored Telecom Calls Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', margin: 0 }}>Active Telecom Calls on PBX Trunk</h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>Live SIP/RTP audio streams being monitored in real time</p>
          </div>
          <span style={{ fontSize: '12px', padding: '3px 10px', borderRadius: '20px', background: 'rgba(6,182,212,0.15)', color: '#06B6D4', fontWeight: '700' }}>
            {activeCalls.length} Active Sessions
          </span>
        </div>

        {actionMessage && (
          <div style={{ padding: '12px', borderRadius: '8px', background: 'rgba(16,185,129,0.15)', border: '1px solid #10B981', color: '#10B981', marginBottom: '16px', fontSize: '13px' }}>
            {actionMessage.message}
          </div>
        )}

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px 12px' }}>Call SID</th>
                <th style={{ padding: '10px 12px' }}>Caller ANI</th>
                <th style={{ padding: '10px 12px' }}>Carrier / Codec</th>
                <th style={{ padding: '10px 12px' }}>STIR/SHAKEN</th>
                <th style={{ padding: '10px 12px' }}>Risk Score</th>
                <th style={{ padding: '10px 12px' }}>Status</th>
                <th style={{ padding: '10px 12px', textAlign: 'right' }}>Operator Defense Actions</th>
              </tr>
            </thead>
            <tbody>
              {activeCalls.map((call, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px', fontWeight: '700', color: '#06B6D4' }}>{call.call_sid}</td>
                  <td style={{ padding: '12px' }}>{call.caller_number}</td>
                  <td style={{ padding: '12px' }}>
                    <div>{call.carrier}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{call.codec}</div>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      fontSize: '11px', padding: '2px 8px', borderRadius: '12px',
                      background: call.stir_shaken?.attestation_level === 'A' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                      color: call.stir_shaken?.attestation_level === 'A' ? '#10B981' : '#EF4444',
                      fontWeight: '700'
                    }}>
                      Level {call.stir_shaken?.attestation_level || 'A'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <div style={{
                      fontWeight: '800',
                      color: call.alert_level === 'RED' ? '#EF4444' : call.alert_level === 'YELLOW' ? '#F59E0B' : '#10B981'
                    }}>
                      {call.cumulative_risk} ({call.alert_level})
                    </div>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      fontSize: '11px', padding: '3px 8px', borderRadius: '4px',
                      background: call.status === 'TERMINATED_BY_SIP_BYE' ? 'rgba(239,68,68,0.2)' : call.status === 'DEFLECTED_TO_FRAUD_DESK' ? 'rgba(245,158,11,0.2)' : 'rgba(16,185,129,0.2)',
                      color: call.status === 'TERMINATED_BY_SIP_BYE' ? '#EF4444' : call.status === 'DEFLECTED_TO_FRAUD_DESK' ? '#F59E0B' : '#10B981',
                      fontWeight: '700'
                    }}>
                      {call.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                      <button
                        onClick={() => handleExecuteAction(call.call_sid, "challenge")}
                        title="Inject spoken biometric challenge passphrase"
                        style={{ padding: '6px 10px', borderRadius: '6px', background: 'rgba(6,182,212,0.15)', border: '1px solid #06B6D4', color: '#06B6D4', cursor: 'pointer', fontSize: '11px', fontWeight: '700' }}
                      >
                        Challenge
                      </button>
                      <button
                        onClick={() => handleExecuteAction(call.call_sid, "transfer")}
                        title="Reroute call to Human Fraud Specialist"
                        style={{ padding: '6px 10px', borderRadius: '6px', background: 'rgba(245,158,11,0.15)', border: '1px solid #F59E0B', color: '#F59E0B', cursor: 'pointer', fontSize: '11px', fontWeight: '700' }}
                      >
                        Transfer
                      </button>
                      <button
                        onClick={() => handleExecuteAction(call.call_sid, "terminate")}
                        title="Send SIP BYE to drop call"
                        style={{ padding: '6px 10px', borderRadius: '6px', background: 'rgba(239,68,68,0.15)', border: '1px solid #EF4444', color: '#EF4444', cursor: 'pointer', fontSize: '11px', fontWeight: '700' }}
                      >
                        Drop (BYE)
                      </button>
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
