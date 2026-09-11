import React, { useState, useEffect } from 'react';
import { ShieldCheck, Lock, Check, Info } from 'lucide-react';

export default function ConsentBanner({ onConsentGiven }) {
  const [hasConsented, setHasConsented] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('dhvani_user_consent');
    if (saved === 'granted') {
      setHasConsented(true);
      if (onConsentGiven) onConsentGiven(true);
    }
  }, [onConsentGiven]);

  const handleGrantConsent = () => {
    localStorage.setItem('dhvani_user_consent', 'granted');
    setHasConsented(true);
    if (onConsentGiven) onConsentGiven(true);
  };

  if (hasConsented) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '16px',
      left: '50%',
      transform: 'translateX(-50%)',
      width: '92%',
      maxWidth: '720px',
      background: '#0B0F19',
      border: '1.5px solid #06B6D4',
      borderRadius: '16px',
      padding: '20px',
      zIndex: 1000,
      boxShadow: '0 10px 40px rgba(6, 182, 212, 0.25)',
      backdropFilter: 'blur(16px)'
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
        <div style={{
          padding: '10px',
          borderRadius: '12px',
          background: 'rgba(6, 182, 212, 0.15)',
          color: '#06B6D4',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <ShieldCheck size={24} />
        </div>

        <div style={{ flex: 1 }}>
          <h4 style={{ fontSize: '15px', fontWeight: '800', margin: '0 0 6px 0', color: '#FFF', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Data Privacy & Audio Processing Consent (DPDP Act 2023)
          </h4>
          
          <p style={{ fontSize: '12px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
            Dhvani Rakshak analyzes voice audio in real-time to detect AI deepfake fraud. 
            <strong> Zero raw audio is stored on servers.</strong> Audio is processed in volatile memory and deleted immediately after inference.
          </p>

          {showDetails && (
            <div style={{ marginTop: '12px', padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', fontSize: '11px', color: '#D1D5DB', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div>• <strong>Indian DPDP Act 2023 Compliant:</strong> No user biometric audio saved.</div>
              <div>• <strong>Memory-Only Processing:</strong> Ingested audio buffers are wiped immediately.</div>
              <div>• <strong>Audit Integrity:</strong> Only SHA-256 cryptographic hashes and numeric risk scores are logged.</div>
            </div>
          )}

          <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
            <button
              onClick={() => setShowDetails(!showDetails)}
              style={{ background: 'transparent', border: 'none', color: '#06B6D4', fontSize: '12px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', padding: 0 }}
            >
              <Info size={14} /> {showDetails ? 'Hide Privacy Details' : 'View Privacy Details'}
            </button>

            <button
              onClick={handleGrantConsent}
              style={{
                padding: '8px 20px',
                borderRadius: '20px',
                background: 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
                color: '#FFF',
                fontWeight: '700',
                fontSize: '13px',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 4px 14px rgba(6, 182, 212, 0.35)'
              }}
            >
              <Check size={16} /> I Consent & Accept
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
