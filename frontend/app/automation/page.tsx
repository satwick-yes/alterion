export default function AutomationPage() {
  return (
    <div style={{ padding: '20px' }}>
      <h2 className="panel-header" style={{ textAlign: 'left', fontSize: '2rem' }}>Natural language cron scheduling</h2>
      
      <div className="panel-container" style={{ marginTop: '20px', minHeight: '400px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        
        <div style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid #00f3ff', borderRadius: '8px', padding: '20px 40px', position: 'relative', boxShadow: '0 0 20px rgba(0,243,255,0.2)' }}>
          <div style={{ position: 'absolute', top: '-10px', left: '20px', background: '#020c1b', padding: '0 10px', color: '#00f3ff', fontSize: '0.8rem', letterSpacing: '1px' }}>INTENT</div>
          <p style={{ color: '#e6f1ff', fontSize: '1.2rem', letterSpacing: '1px' }}>Run backup every Friday at midnight</p>
        </div>
        
        <div style={{ margin: '30px 0', width: '2px', height: '40px', background: 'linear-gradient(to bottom, #00f3ff, transparent)' }}></div>
        
        <div style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(0,243,255,0.4)', borderRadius: '8px', padding: '20px 40px', position: 'relative', minWidth: '350px', textAlign: 'center' }}>
          <div style={{ position: 'absolute', top: '-10px', left: '20px', background: '#020c1b', padding: '0 10px', color: '#8892b0', fontSize: '0.8rem', letterSpacing: '1px' }}>CRON EXPRESSION</div>
          <p className="glowing-text" style={{ fontSize: '1.5rem', fontFamily: 'monospace', letterSpacing: '5px' }}>0 0 * * 5</p>
        </div>
        
        <button className="cyan-btn" style={{ marginTop: '50px' }}>ACTIVATE SCHEDULE</button>

      </div>
    </div>
  );
}