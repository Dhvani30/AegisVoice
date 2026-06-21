import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  const removeAlert = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  useEffect(() => {
    let ws = null;
    let reconnectTimer = null;

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
            const newAlert = {
              id: Date.now(),
              ...data,
              createdAt: Date.now()
            };
            
            setAlerts(prev => [newAlert, ...prev]);
            
            // Auto-remove after 30 seconds
            setTimeout(() => {
              removeAlert(newAlert.id);
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
      if (ws) ws.close();
    };
  }, []);

  if (!wsConnected) {
    return (
      <div className="connection-status">
        <div className="status-content">
          <div className="spinner" />
          <h3>Aegis Voice</h3>
          <p>Establishing secure connection...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="overlay-container">
      {alerts.length > 0 && <div className="pulsing-border" />}
      
      <div className="alerts-container">
        {alerts.map((alert, index) => (
          <AlertCard 
            key={alert.id} 
            alert={alert} 
            onClose={() => removeAlert(alert.id)}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}

// Separate component for individual alert cards
function AlertCard({ alert, onClose, index }) {
  return (
    <div className="alert-card" style={{ '--delay': `${index * 0.1}s` }}>
      <div className="alert-header">
        <div className="alert-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
        <div className="alert-title-section">
          <h2>AEGIS VOICE</h2>
          <span className="alert-badge">HIGH RISK SCAM DETECTED</span>
        </div>
        <button className="close-btn" onClick={onClose} title="Dismiss alert">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
      
      <div className="alert-body">
        <p className="alert-reason">{alert.reason}</p>
        
        <div className="alert-footer">
          <div className="risk-meter">
            <div className="risk-label">Risk Score</div>
            <div className="risk-bar-container">
              <div 
                className="risk-bar" 
                style={{ width: `${alert.risk_score}%` }}
              />
            </div>
            <div className="risk-value">{alert.risk_score}/100</div>
          </div>
          
          <div className="alert-timer">
            <div className="timer-bar" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;