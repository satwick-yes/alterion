export default function ChatPage() {
  return (
    <div style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h2 className="panel-header" style={{ textAlign: 'left', fontSize: '2rem' }}>AI Chat with inline tool results</h2>
      
      <div className="panel-container" style={{ flex: 1, marginTop: '20px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
          
          <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(0, 243, 255, 0.2)', border: '1px solid #00f3ff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#00f3ff' }}>A</div>
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '10px', maxWidth: '80%' }}>
              <p style={{ color: '#e6f1ff', fontSize: '0.9rem', lineHeight: '1.5' }}>Here is the Q1 sales report. Forecast looks promising.</p>
              
              <div style={{ marginTop: '20px', background: 'rgba(0,0,0,0.5)', padding: '15px', borderRadius: '8px', border: '1px solid rgba(0, 243, 255, 0.2)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#8892b0', fontSize: '0.8rem', marginBottom: '15px' }}>
                  <span>Q1 SALES (EST)</span>
                  <span>MARKET SHARE</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '10px', height: '80px' }}>
                  <div style={{ width: '30px', background: '#00f3ff', height: '40%', boxShadow: '0 0 10px rgba(0,243,255,0.4)' }}></div>
                  <div style={{ width: '30px', background: '#00f3ff', height: '55%', boxShadow: '0 0 10px rgba(0,243,255,0.4)' }}></div>
                  <div style={{ width: '30px', background: '#00f3ff', height: '70%', boxShadow: '0 0 10px rgba(0,243,255,0.4)' }}></div>
                  <div style={{ width: '30px', background: '#00f3ff', height: '85%', boxShadow: '0 0 10px rgba(0,243,255,0.4)' }}></div>
                  <div style={{ width: '30px', background: '#00f3ff', height: '100%', boxShadow: '0 0 10px rgba(0,243,255,0.4)' }}></div>
                  <div style={{ flex: 1 }}></div>
                  <div style={{ width: '60px', height: '60px', borderRadius: '50%', border: '8px solid #00f3ff', borderTopColor: 'transparent', transform: 'rotate(45deg)' }}></div>
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '15px', justifyContent: 'flex-end', marginBottom: '30px' }}>
            <div style={{ background: 'rgba(0, 243, 255, 0.1)', border: '1px solid rgba(0, 243, 255, 0.3)', padding: '15px', borderRadius: '10px', maxWidth: '80%' }}>
              <p style={{ color: '#00f3ff', fontSize: '0.9rem' }}>Show me Q1 sales data and forecast.</p>
            </div>
            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(255, 255, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>U</div>
          </div>
          
        </div>
        
        <div style={{ display: 'flex', gap: '15px', marginTop: '10px' }}>
          <input type="text" placeholder="Type a message..." style={{ flex: 1, background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(0,243,255,0.3)', borderRadius: '20px', padding: '15px 20px', color: '#fff', outline: 'none' }} />
          <button style={{ background: '#00f3ff', border: 'none', borderRadius: '50%', width: '50px', height: '50px', cursor: 'pointer', boxShadow: '0 0 15px rgba(0,243,255,0.5)' }}>&gt;</button>
        </div>
      </div>
    </div>
  );
}