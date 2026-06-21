import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [alert, setAlert] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    let ws = null;
    let reconnectTimer = null;
    let alertTimer = null;

    const connectWebSocket = () => {
      console.log('Attempting WebSocket connection...');
      ws = new WebSocket('ws://127.0.0.1:8765');
      
      ws.onopen = () => {
        console.log('WebSocket connected successfully!');
        setWsConnected(true);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Alert received:', data);
          
          if (data.type === 'SCAM_ALERT') {
            // Clear any existing alert timer
            if (alertTimer) clearTimeout(alertTimer);
            
            // Show new alert (replaces previous one)
            setAlert(data);
            
            // Auto-hide after 30 seconds (increased from 10)
            alertTimer = setTimeout(() => {
              setAlert(null);
            }, 30000);
          }
        } catch (e) { 
          console.error("WS Parse Error", e); 
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        
        reconnectTimer = setTimeout(connectWebSocket, 2000);
      };
    };

    connectWebSocket();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (alertTimer) clearTimeout(alertTimer);
      if (ws) ws.close();
    };
  }, []);

  // Manual close function
  const closeAlert = () => {
    setAlert(null);
  };

  if (!wsConnected) {
    return (
      <div style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        background: 'rgba(0,0,0,0.8)',
        color: 'white',
        padding: '20px',
        borderRadius: '8px',
        fontFamily: 'system-ui',
        zIndex: 999999
      }}>
        <h3>Aegis Voice</h3>
        <p>Connecting to backend...</p>
      </div>
    );
  }

  if (!alert) return null;

  return (
    <div className="overlay-container">
      <div className="pulsing-border" />
      
      <div className="toast">
        <button className="close-btn" onClick={closeAlert} title="Close alert">×</button>
        <h2> AEGIS VOICE: HIGH RISK SCAM DETECTED</h2>
        <p>{alert.reason}</p>
        <div className="score">Risk Score: {alert.risk_score}/100</div>
      </div>
    </div>
  );
}

export default App;