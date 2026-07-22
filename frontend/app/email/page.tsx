export default function EmailPage() {
  return (
    <div style={{ padding: '20px' }}>
      <h2 className="panel-header" style={{ textAlign: 'left', fontSize: '2rem' }}>Smart Email Archiving Logic</h2>
      <div className="panel-container" style={{ marginTop: '20px', minHeight: '500px', display: 'flex' }}>
        
        {/* Sidebar */}
        <div style={{ width: '200px', borderRight: '1px solid rgba(0,243,255,0.2)', paddingRight: '20px' }}>
          <h3 style={{ color: '#e6f1ff', marginBottom: '20px', fontSize: '1.2rem' }}>Inbox</h3>
          <div style={{ color: '#00f3ff', background: 'rgba(0,243,255,0.1)', padding: '10px', borderRadius: '5px', marginBottom: '10px' }}>&gt; Inbox</div>
          <div style={{ color: '#8892b0', padding: '10px', marginBottom: '10px' }}>Supporting</div>
          <div style={{ color: '#8892b0', padding: '10px', marginBottom: '10px' }}>Messages</div>
          <div style={{ color: '#8892b0', padding: '10px', marginBottom: '10px' }}>Rules</div>
          <div style={{ marginTop: 'auto', paddingTop: '50px', color: '#00f3ff', fontSize: '0.8rem' }}>Rules Active: 14</div>
        </div>
        
        {/* Logic Flow */}
        <div style={{ flex: 1, paddingLeft: '40px', position: 'relative' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '30px', background: 'rgba(0,243,255,0.05)', padding: '15px', borderRadius: '8px', borderLeft: '3px solid #00f3ff' }}>
            <div>
              <div style={{ color: '#e6f1ff', fontWeight: 'bold' }}>Meeting Memos</div>
              <div style={{ color: '#8892b0', fontSize: '0.8rem' }}>Contains "meeting notes" or "minutes"</div>
            </div>
            <div style={{ marginLeft: 'auto', width: '40px', height: '2px', background: '#00f3ff', position: 'relative' }}>
              <div style={{ position: 'absolute', right: 0, top: '-4px', width: '10px', height: '10px', borderTop: '2px solid #00f3ff', borderRight: '2px solid #00f3ff', transform: 'rotate(45deg)' }}></div>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '30px', padding: '15px' }}>
            <div>
              <div style={{ color: '#e6f1ff', fontWeight: 'bold' }}>Client Proposal</div>
              <div style={{ color: '#8892b0', fontSize: '0.8rem' }}>Domain @clientagency.com</div>
            </div>
            <div style={{ marginLeft: 'auto', width: '40px', height: '2px', background: '#00f3ff', position: 'relative' }}>
              <div style={{ position: 'absolute', right: 0, top: '-4px', width: '10px', height: '10px', borderTop: '2px solid #00f3ff', borderRight: '2px solid #00f3ff', transform: 'rotate(45deg)' }}></div>
            </div>
          </div>

          <div style={{ position: 'absolute', right: '40px', top: '20px', display: 'flex', gap: '30px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ width: '60px', height: '50px', border: '2px solid #00f3ff', borderRadius: '5px', marginBottom: '10px', boxShadow: '0 0 10px rgba(0,243,255,0.3)' }}></div>
              <span style={{ color: '#00f3ff', fontSize: '0.8rem', textTransform: 'uppercase' }}>Archive</span>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ width: '60px', height: '50px', border: '2px solid #00f3ff', borderRadius: '5px', marginBottom: '10px', boxShadow: '0 0 10px rgba(0,243,255,0.3)' }}></div>
              <span style={{ color: '#00f3ff', fontSize: '0.8rem', textTransform: 'uppercase' }}>Clients</span>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ width: '60px', height: '50px', border: '2px solid #00f3ff', borderRadius: '5px', marginBottom: '10px', boxShadow: '0 0 10px rgba(0,243,255,0.3)' }}></div>
              <span style={{ color: '#00f3ff', fontSize: '0.8rem', textTransform: 'uppercase' }}>Projects</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}