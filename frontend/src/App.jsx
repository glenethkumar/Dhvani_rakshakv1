import React, { useState } from 'react';
import { Menu, X, Waves, PhoneCall, Cpu, Eye, ShieldCheck, Sliders, FileText, Zap, ChevronRight, Search, Shield, HelpCircle } from 'lucide-react';
import LiveMonitor from './components/LiveMonitor';
import CallSimulator from './components/CallSimulator';
import ExecutiveDashboard from './components/ExecutiveDashboard';
import VoiceEnrollment from './components/VoiceEnrollment';
import PolicyConfig from './components/PolicyConfig';
import ComplianceAudit from './components/ComplianceAudit';
import ExplainabilityDashboard from './components/ExplainabilityDashboard';
import HowItWorks from './components/HowItWorks';
import ConsentBanner from './components/ConsentBanner';

export default function App() {
  const [activeTab, setActiveTab] = useState('monitor');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    {
      name: '🛡️ Core Detection Engine',
      items: [
        { id: 'monitor', label: 'Live Monitor', icon: Waves, simpleDesc: 'Real-time live microphone stream AI voice detection scanner.' },
        { id: 'simulator', label: 'Call Simulator', icon: PhoneCall, simpleDesc: 'Simulates real vs AI-cloned voice calls.' },
        { id: 'xai', label: 'Explainable AI', icon: Eye, simpleDesc: 'Forensic acoustic analysis showing reasons why a voice was flagged.' },
        { id: 'howitworks', label: 'How It Works', icon: HelpCircle, simpleDesc: 'Interactive processing pipeline diagram.' }
      ]
    },
    {
      name: '📊 Dashboard & Controls',
      items: [
        { id: 'dashboard', label: 'Executive Dashboard', icon: Cpu, simpleDesc: 'Overview of total calls scanned, accuracy, and latency metrics.' },
        { id: 'enrollment', label: 'Voice Enrollment', icon: ShieldCheck, simpleDesc: 'Register genuine voice biometrics without storing raw audio.' },
        { id: 'policy', label: 'Policy Configuration', icon: Sliders, simpleDesc: 'Adjust risk threshold sensitivity and model weights.' },
        { id: 'audit', label: 'Compliance Audit Logs', icon: FileText, simpleDesc: 'DPDP Act 2023 zero-raw-audio retention audit trail.' }
      ]
    }
  ];

  const filteredCategories = categories.map(cat => ({
    ...cat,
    items: cat.items.filter(item => 
      item.label.toLowerCase().includes(searchQuery.toLowerCase()) || 
      item.simpleDesc.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(cat => cat.items.length > 0);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#07090E', color: '#F3F4F6', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      
      {/* Top Header */}
      <header style={{
        background: 'rgba(11, 15, 25, 0.95)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        padding: '0 16px',
        height: '64px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        {/* Left Side: Menu Toggle + Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: isMenuOpen ? 'rgba(6, 182, 212, 0.25)' : 'rgba(255, 255, 255, 0.06)',
              border: isMenuOpen ? '1.5px solid #06B6D4' : '1px solid rgba(255, 255, 255, 0.12)',
              color: isMenuOpen ? '#06B6D4' : '#FFF',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            title="Open Features Menu"
          >
            {isMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '36px', height: '36px', borderRadius: '10px',
              background: 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Zap size={20} color="#FFF" />
            </div>
            <div>
              <h1 style={{ fontSize: '16px', fontWeight: '800', letterSpacing: '-0.5px', background: 'linear-gradient(90deg, #FFF 0%, #9CA3AF 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>
                DHVANI RAKSHAK
              </h1>
              <div style={{ fontSize: '9px', color: '#06B6D4', fontWeight: '700', letterSpacing: '0.5px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>AI VOICE CLONE DEFENSE</span>
                <span style={{ background: 'rgba(16, 185, 129, 0.2)', border: '1px solid #10B981', color: '#10B981', padding: '1px 5px', borderRadius: '4px', fontSize: '8px' }}>v2.4 VOICE CONVERSION ACTIVE</span>
              </div>
            </div>
          </div>
        </div>

        {/* Top Quick Navigation Tabs */}
        <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', padding: '4px 0' }}>
          {[
            { id: 'monitor', label: 'Live Monitor' },
            { id: 'simulator', label: 'Call Simulator' },
            { id: 'xai', label: 'Explainable AI' },
            { id: 'enrollment', label: 'Voice Enrollment' },
            { id: 'policy', label: 'Policy Configuration' },
            { id: 'dashboard', label: 'Executive Dashboard' },
            { id: 'audit', label: 'Compliance Audit Logs' }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                border: activeTab === t.id ? '1px solid #06B6D4' : '1px solid transparent',
                background: activeTab === t.id ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                color: activeTab === t.id ? '#06B6D4' : '#9CA3AF',
                fontSize: '12px',
                fontWeight: '700',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      {/* Navigation Drawer */}
      {isMenuOpen && (
        <div 
          onClick={() => setIsMenuOpen(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(8px)', zIndex: 200, display: 'flex' }}
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            style={{
              width: '340px',
              maxWidth: '85vw',
              height: '100%',
              background: '#0B0F19',
              borderRight: '1px solid rgba(255, 255, 255, 0.1)',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              overflowY: 'auto'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '14px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '800', margin: 0, color: '#06B6D4', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Shield size={18} /> Menu Navigation
                </h3>
              </div>
              <button 
                onClick={() => setIsMenuOpen(false)}
                style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '6px', color: '#9CA3AF', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ position: 'relative' }}>
              <Search size={16} color="#6B7280" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                placeholder="Search features..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px 8px 36px',
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  color: '#FFF',
                  fontSize: '13px',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {filteredCategories.map((cat, idx) => (
                <div key={idx}>
                  <div style={{ fontSize: '11px', fontWeight: '800', color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: '8px' }}>
                    {cat.name}
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {cat.items.map(item => {
                      const Icon = item.icon;
                      const isActive = activeTab === item.id;
                      return (
                        <div
                          key={item.id}
                          onClick={() => {
                            setActiveTab(item.id);
                            setIsMenuOpen(false);
                          }}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px',
                            padding: '10px',
                            borderRadius: '10px',
                            background: isActive ? 'rgba(6, 182, 212, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                            border: isActive ? '1px solid rgba(6, 182, 212, 0.4)' : '1px solid rgba(255, 255, 255, 0.05)',
                            cursor: 'pointer'
                          }}
                        >
                          <div style={{
                            padding: '6px',
                            borderRadius: '6px',
                            background: isActive ? '#06B6D4' : 'rgba(255, 255, 255, 0.05)',
                            color: isActive ? '#FFF' : '#06B6D4'
                          }}>
                            <Icon size={16} />
                          </div>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontWeight: '700', fontSize: '13px', color: isActive ? '#06B6D4' : '#F3F4F6' }}>
                                {item.label}
                              </span>
                              <ChevronRight size={14} color={isActive ? '#06B6D4' : '#6B7280'} />
                            </div>
                            <p style={{ fontSize: '11px', color: 'var(--text-muted)', margin: '2px 0 0 0', lineHeight: '1.3' }}>
                              {item.simpleDesc}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* DPDP Act 2023 Consent Overlay Banner */}
      <ConsentBanner />

      {/* Main View Container */}
      <main style={{ flex: 1, padding: '16px', maxWidth: '1200px', width: '100%', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px', paddingBottom: '24px' }}>
        {activeTab === 'monitor' && <LiveMonitor />}
        {activeTab === 'simulator' && <CallSimulator />}
        {activeTab === 'xai' && <ExplainabilityDashboard />}
        {activeTab === 'howitworks' && <HowItWorks />}
        {activeTab === 'dashboard' && <ExecutiveDashboard />}
        {activeTab === 'enrollment' && <VoiceEnrollment />}
        {activeTab === 'policy' && <PolicyConfig />}
        {activeTab === 'audit' && <ComplianceAudit />}
      </main>

    </div>
  );
}
