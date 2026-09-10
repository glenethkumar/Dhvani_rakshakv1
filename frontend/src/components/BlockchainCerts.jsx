import React, { useState } from 'react';
import { Database, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function BlockchainCerts() {
  const [certs, setCerts] = useState([
    {
      id: "VOICE_PASS_0x89F4B321",
      speaker: "Rajesh Sharma (CEO)",
      contract: "0x7F99a4B8e1208D12942C8b10959B4a32",
      block: 104821,
      network: "Polygon Blockchain / Web3",
      merkleHash: "e3b0c44298fc1c149afbf4c8996fb924",
      issuedAt: "2026-09-01T10:00:00Z",
      status: "AUTHENTIC & VERIFIED ON BLOCKCHAIN"
    },
    {
      id: "VOICE_PASS_0x33B109C4",
      speaker: "Priya Nair (CFO)",
      contract: "0x7F99a4B8e1208D12942C8b10959B4a32",
      block: 104818,
      network: "Polygon Blockchain / Web3",
      merkleHash: "8f434346648f6b96df89dda901c5176b",
      issuedAt: "2026-08-28T14:30:00Z",
      status: "AUTHENTIC & VERIFIED ON BLOCKCHAIN"
    }
  ]);

  const [newSpeaker, setNewSpeaker] = useState("Anand Verma (Director)");
  const [issuing, setIssuing] = useState(false);

  const handleIssueCert = () => {
    setIssuing(true);
    setTimeout(() => {
      setIssuing(false);
      const newCert = {
        id: `VOICE_PASS_0x${Math.random().toString(16).substring(2, 10).toUpperCase()}`,
        speaker: newSpeaker,
        contract: "0x7F99a4B8e1208D12942C8b10959B4a32",
        block: 104825,
        network: "Polygon Blockchain / Web3",
        merkleHash: "5d41402abc4b2a76b9719d911017c592",
        issuedAt: new Date().toISOString(),
        status: "AUTHENTIC & VERIFIED ON BLOCKCHAIN"
      };
      setCerts([newCert, ...certs]);
    }, 800);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '6px' }}>Digital Voice Pass & Blockchain Certificates</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: 0 }}>
            <strong>What it does:</strong> Creates tamper-proof digital certificates on a secure blockchain ledger so authentic voice registrations can be legally verified in court.
          </p>
        </div>
        <div style={{ padding: '8px 16px', borderRadius: '20px', background: 'rgba(16, 185, 129, 0.15)', color: '#10B981', border: '1px solid rgba(16, 185, 129, 0.3)', fontSize: '13px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Database size={16} /> Polygon Blockchain Verified
        </div>
      </div>

      {/* Hero Image Banner */}
      <div className="image-banner-card" style={{ height: '220px', position: 'relative' }}>
        <img 
          src="/images/feature_blockchain.jpg" 
          onError={(e) => { e.currentTarget.src = "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=1200&q=80"; }} 
          alt="Immutable Cryptographic Blockchain Ledger" 
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(7, 9, 14, 0.1) 0%, rgba(7, 9, 14, 0.85) 100%)',
          display: 'flex', alignItems: 'flex-end', padding: '24px'
        }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: '800', color: '#10B981', textTransform: 'uppercase', letterSpacing: '1px' }}>
              🔗 Cryptographic Identity Chain
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '800', color: '#FFF', margin: '4px 0' }}>
              Immutable Merkle Tree Voice Verification & Decentralized Passport
            </h3>
            <p style={{ fontSize: '12px', color: '#D1D5DB', margin: 0 }}>
              Tamper-proof cryptographic hashes stamped on Polygon network for zero-trust legal non-repudiation.
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Issue Digital Voice Pass</h3>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>PERSON NAME & POSITION</label>
            <input
              type="text" value={newSpeaker} onChange={(e) => setNewSpeaker(e.target.value)}
              style={{ width: '100%', padding: '12px', borderRadius: '8px', background: '#0A0D14', color: '#FFF', border: '1px solid rgba(255,255,255,0.15)', fontSize: '14px' }}
            />
          </div>
          <button
            onClick={handleIssueCert}
            disabled={issuing}
            style={{ padding: '12px', borderRadius: '8px', background: '#10B981', color: '#FFF', fontWeight: '700', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {issuing ? 'Writing to Blockchain...' : 'Create Digital Voice Pass'}
          </button>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>Verified Digital Voice Passes</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {certs.map((c, idx) => (
              <div key={idx} style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontWeight: '700', fontSize: '15px', color: '#06B6D4', fontFamily: 'JetBrains Mono' }}>{c.id}</span>
                  <span style={{ padding: '2px 8px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.2)', color: '#10B981', fontWeight: '700', fontSize: '11px' }}>
                    {c.status}
                  </span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '4px' }}>Person: {c.speaker}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>Smart Contract: {c.contract} • Block #{c.block}</div>
                <div style={{ fontSize: '11px', color: '#9CA3AF', fontFamily: 'JetBrains Mono', marginTop: '4px' }}>Digital Voice Fingerprint Hash: {c.merkleHash}...</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
