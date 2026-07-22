export default function CalendarPage() {
  const days = Array.from({length: 30}, (_, i) => i + 1);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 className="panel-header" style={{ textAlign: 'left', fontSize: '2rem' }}>Calendar & Scheduling</h2>
      
      <div className="panel-container" style={{ marginTop: '20px', display: 'flex', gap: '30px' }}>
        
        {/* Calendar Grid */}
        <div style={{ flex: 2 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 className="glowing-text" style={{ fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '2px' }}>September 2026</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="cyan-btn">&lt;</button>
              <button className="cyan-btn">&gt;</button>
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '10px', textAlign: 'center', color: '#8892b0', fontSize: '0.8rem', marginBottom: '10px' }}>
            <div>SUN</div><div>MON</div><div>TUE</div><div>WED</div><div>THU</div><div>FRI</div><div>SAT</div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '10px' }}>
            {days.map(d => (
              <div key={d} style={{ 
                height: '60px', 
                background: 'rgba(0,0,0,0.3)', 
                border: d === 15 ? '1px solid #00f3ff' : '1px solid rgba(255,255,255,0.05)',
                boxShadow: d === 15 ? '0 0 10px rgba(0,243,255,0.4) inset' : 'none',
                display: 'flex', 
                flexDirection: 'column',
                padding: '5px'
              }}>
                <span style={{ color: d === 15 ? '#00f3ff' : '#e6f1ff', fontSize: '0.9rem' }}>{d}</span>
                {d === 10 && <div style={{ background: '#00f3ff', height: '4px', width: '80%', margin: 'auto', borderRadius: '2px' }}></div>}
                {d === 22 && <div style={{ background: '#ff3333', height: '4px', width: '80%', margin: 'auto', borderRadius: '2px' }}></div>}
              </div>
            ))}
          </div>
        </div>
        
        {/* Upcoming Events */}
        <div style={{ flex: 1, borderLeft: '1px solid rgba(0,243,255,0.2)', paddingLeft: '30px' }}>
          <h3 style={{ color: '#8892b0', fontSize: '0.9rem', marginBottom: '20px', textTransform: 'uppercase', letterSpacing: '1px' }}>Upcoming Events</h3>
          
          <div style={{ background: 'rgba(0,243,255,0.1)', padding: '15px', borderRadius: '8px', borderLeft: '3px solid #00f3ff', marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e6f1ff', fontWeight: 'bold' }}>Product Launch</span>
              <span style={{ color: '#00f3ff', fontSize: '0.8rem' }}>1:30 PM</span>
            </div>
            <div style={{ color: '#8892b0', fontSize: '0.8rem', marginTop: '5px' }}>Presentation room A</div>
          </div>
          
          <div style={{ padding: '15px', borderRadius: '8px', borderLeft: '3px solid #8892b0', marginBottom: '15px', background: 'rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e6f1ff', fontWeight: 'bold' }}>Team Sync</span>
              <span style={{ color: '#8892b0', fontSize: '0.8rem' }}>2:00 PM</span>
            </div>
          </div>
          
          <div style={{ padding: '15px', borderRadius: '8px', borderLeft: '3px solid #8892b0', marginBottom: '15px', background: 'rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#e6f1ff', fontWeight: 'bold' }}>Client Review</span>
              <span style={{ color: '#8892b0', fontSize: '0.8rem' }}>4:00 PM</span>
            </div>
          </div>
          
          <button className="cyan-btn" style={{ width: '100%', marginTop: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.2rem' }}>+</span> SCHEDULE WITH VOICE
          </button>
        </div>
        
      </div>
    </div>
  );
}