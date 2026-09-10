import React, { useState } from 'react';
import { Menu, X, Waves, PhoneCall, Cpu, Eye, Award, Database, HeartPulse, ShieldCheck, Sliders, FileText, Zap, ChevronRight, Search, Shield, Radio } from 'lucide-react';
import LiveMonitor from './components/LiveMonitor';
import CallSimulator from './components/CallSimulator';
import ExecutiveDashboard from './components/ExecutiveDashboard';
import VoiceEnrollment from './components/VoiceEnrollment';
import PolicyConfig from './components/PolicyConfig';
import ComplianceAudit from './components/ComplianceAudit';
import ExplainabilityDashboard from './components/ExplainabilityDashboard';
import GovVipProtection from './components/GovVipProtection';
import BlockchainCerts from './components/BlockchainCerts';
import BehavioralBiometrics from './components/BehavioralBiometrics';
import TelecomGateway from './components/TelecomGateway';

export default function App() {
  const [activeTab, setActiveTab] = useState('telecom');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    {
      name: '🛡️ Voice Call Protection',
      items: [
        { id: 'telecom', label: 'Phone Line Interceptor', icon: Radio, simpleDesc: 'Auto-scans phone calls and blocks fake AI voices.' },
        { id: 'monitor', label: 'Live Voice Scanner', icon: Waves, simpleDesc: 'Checks live microphone audio and alerts you if a voice is fake.' },
        { id: 'simulator', label: 'Voice Fake Simulator', icon: PhoneCall, simpleDesc: 'Test how fake voices and scam calls are detected.' },
        { id: 'dashboard', label: 'Security Overview', icon: Cpu, simpleDesc: 'See total calls scanned, blocked scam attempts, and money saved.' }
      ]
    },
    {
      name: '🔍 Voice Analysis & Safety',
      items: [
        { id: 'xai', label: 'Why Is It Fake?', icon: Eye, simpleDesc: 'Simple explanations showing why a call was marked fake.' },
        { id: 'gov', label: 'VIP Protection', icon: Award, simpleDesc: 'Extra safety mode for leaders, executives, and bank accounts.' },
        { id: 'blockchain', label: 'Digital Voice Pass', icon: Database, simpleDesc: 'Creates secure voice certificates for official proof.' },
        { id: 'behavioral', label: 'Behavior Check', icon: HeartPulse, simpleDesc: 'Checks caller stress, odd call times, and unusual habits.' }
      ]
    },
    {
      name: '⚙️ Settings & Privacy',
      items: [
        { id: 'enrollment', label: 'Register Voice', icon: ShieldCheck, simpleDesc: 'Safely save your real voice profile without storing audio.' },
        { id: 'policy', label: 'System Settings', icon: Sliders, simpleDesc: 'Change risk sensitivity and auto-block rules.' },
        { id: 'audit', label: 'Safety Reports', icon: FileText, simpleDesc: 'Clear privacy reports proving 100% data safety.' }
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
        {/* Left Side: 3-Line Menu Drawer Toggle Button + Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          
          {/* 3-Line Hamburger Menu Button (≡) */}
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

          {/* Logo & Platform Name */}
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
              <div style={{ fontSize: '9px', color: '#06B6D4', fontWeight: '700', letterSpacing: '0.5px' }}>
                AI VOICE CLONE DEFENSE
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Android Call Interceptor Button & Active Engine Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => {
              if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.CallDetector) {
                window.Capacitor.Plugins.CallDetector.requestCallPermissions();
                alert("Android Auto Call Interceptor Enabled! Floating risk badge will show on incoming calls.");
              } else {
                alert("Android Call Interceptor Plugin Active. Run app in Android Studio to experience live floating badge during phone calls!");
              }
            }}
            style={{
              display: 'flex', alignItems: 'center', gap: '5px', fontSize: '11px', fontWeight: '700',
              color: '#06B6D4', background: 'rgba(6, 182, 212, 0.12)', padding: '6px 12px',
              borderRadius: '20px', border: '1px solid rgba(6, 182, 212, 0.3)', cursor: 'pointer', whiteSpace: 'nowrap'
            }}
          >
            <Radio size={13} /> Auto Interceptor
          </button>
        </div>
      </header>

      {/* 3-Line Menu Navigation Drawer */}
      {isMenuOpen && (
        <div 
          onClick={() => setIsMenuOpen(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(8px)', zIndex: 200, display: 'flex' }}
        >
          {/* Drawer Sidebar */}
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
            {/* Drawer Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '14px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '800', margin: 0, color: '#06B6D4', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Shield size={18} /> Application Features
                </h3>
                <p style={{ fontSize: '11px', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>Tap any feature to open</p>
              </div>
              <button 
                onClick={() => setIsMenuOpen(false)}
                style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '6px', color: '#9CA3AF', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Search Input */}
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

            {/* Feature Categories */}
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

      {/* Main View Container */}
      <main style={{ flex: 1, padding: '16px', maxWidth: '1200px', width: '100%', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px', paddingBottom: '24px' }}>

        {activeTab === 'telecom' && <TelecomGateway />}
        {activeTab === 'monitor' && <LiveMonitor />}
        {activeTab === 'simulator' && <CallSimulator />}
        {activeTab === 'dashboard' && <ExecutiveDashboard />}
        {activeTab === 'xai' && <ExplainabilityDashboard />}
        {activeTab === 'gov' && <GovVipProtection />}
        {activeTab === 'blockchain' && <BlockchainCerts />}
        {activeTab === 'behavioral' && <BehavioralBiometrics />}
        {activeTab === 'enrollment' && <VoiceEnrollment />}
        {activeTab === 'policy' && <PolicyConfig />}
        {activeTab === 'audit' && <ComplianceAudit />}
      </main>

    </div>
  );
}
