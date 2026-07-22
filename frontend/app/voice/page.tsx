export default function VoicePage() {
  return (
    <div style={{ padding: '20px', height: '100%' }}>
      <h2 className="panel-header" style={{ textAlign: 'left', fontSize: '2rem' }}>Voice as core interaction modality</h2>
      
      <div className="panel-container" style={{ marginTop: '20px', height: 'calc(100% - 100px)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        
        {/* Animated Waveform Mock */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', height: '100px', marginBottom: '40px' }}>
          {Array.from({length: 40}).map((_, i) => (
            <div key={i} style={{
              width: '4px',
              background: '#00f3ff',
              height: `${Math.random() * 80 + 20}%`,
              borderRadius: '2px',
              boxShadow: '0 0 10px #00f3ff',
              opacity: 0.8
            }}></div>
          ))}
        </div>
        
        <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'rgba(0,243,255,0.1)', border: '2px solid #00f3ff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 30px rgba(0,243,255,0.5)', marginBottom: '20px' }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#00f3ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="22"></line>
          </svg>
        </div>
        
        <h3 className="glowing-text" style={{ fontSize: '2rem', letterSpacing: '4px', textTransform: 'uppercase', marginBottom: '40px' }}>HANDS-FREE CONTROL</h3>
        
        <div style={{ background: 'rgba(0,0,0,0.4)', padding: '20px', borderRadius: '10px', border: '1px solid rgba(0,243,255,0.2)', width: '60%' }}>
          <div style={{ textAlign: 'center', color: '#8892b0', fontSize: '0.8rem', letterSpacing: '2px', marginBottom: '20px' }}>VOICE COMMANDS</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div style={{ color: '#e6f1ff', fontSize: '0.9rem', display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <span>Create task</span><span style={{ color: '#00f3ff' }}>&gt;</span>
            </div>
            <div style={{ color: '#e6f1ff', fontSize: '0.9rem', display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <span>Adjust volume</span><span style={{ color: '#00f3ff' }}>&gt;</span>
            </div>
            <div style={{ color: '#e6f1ff', fontSize: '0.9rem', display: 'flex', justifyContent: 'space-between', padding: '10px' }}>
              <span>Search document</span><span style={{ color: '#00f3ff' }}>&gt;</span>
            </div>
            <div style={{ color: '#e6f1ff', fontSize: '0.9rem', display: 'flex', justifyContent: 'space-between', padding: '10px' }}>
              <span>Navigate home</span><span style={{ color: '#00f3ff' }}>&gt;</span>
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
}