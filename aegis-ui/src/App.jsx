import { useState, useEffect, useRef } from 'react';
import './App.css';

// Helper to determine theme, badge, and icon based on risk score
const getAlertConfig = (score) => {
  if (score >= 50) {
    return {
      theme: 'red',
      badge: 'HIGH RISK SCAM DETECTED',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      )
    };
  } else if (score >= 26) {
    return {
      theme: 'orange',
      badge: 'MEDIUM RISK WARNING',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      )
    };
  } else {
    return {
      theme: 'yellow',
      badge: 'LOW RISK ADVISORY',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
      )
    };
  }
};

function App() {
  const [alerts, setAlerts] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);

  useEffect(() => {
    const connectWebSocket = () => {
      // Prevent duplicate connections
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        return;
      }

      console.log('Attempting WebSocket connection...');
      const ws = new WebSocket('ws://127.0.0.1:8765');
      wsRef.current = ws;
      
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
              id: data.id || (Date.now() + Math.random()),
              ...data,
              createdAt: Date.now()
            };
            
            // Deduplicate: check if alert with same ID already exists
            setAlerts(prev => {
              const exists = prev.some(a => a.id === newAlert.id);
              if (exists) return prev;
              return [newAlert, ...prev];
            });
            
            // Auto-remove after 30 seconds
            setTimeout(() => {
              setAlerts(prev => prev.filter(alert => alert.id !== newAlert.id));
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
        
        // Only reconnect if this is still the active connection
        if (wsRef.current === ws) {
          reconnectTimerRef.current = setTimeout(connectWebSocket, 2000);
        }
      };
    };

    connectWebSocket();

    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  const removeAlert = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

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

  // Calculate the highest risk score to determine the screen border color
  const maxRiskScore = alerts.length > 0 ? Math.max(...alerts.map(a => a.risk_score)) : 0;
  const borderTheme = maxRiskScore >= 50 ? 'red' : maxRiskScore >= 26 ? 'orange' : maxRiskScore >= 10 ? 'yellow' : '';

  return (
    <div className="overlay-container">
      {/* Apply dynamic theme class to pulsing border */}
      {alerts.length > 0 && <div className={`pulsing-border theme-${borderTheme}`} />}
      
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

function AlertCard({ alert, onClose, index }) {
  const config = getAlertConfig(alert.risk_score);

  return (
    // Apply dynamic theme class to the card
    <div className={`alert-card theme-${config.theme}`} style={{ '--delay': `${index * 0.1}s` }}>
      <div className="alert-header">
        <div className="alert-icon">
          {config.icon}
        </div>
        <div className="alert-title-section">
          <h2>AEGIS VOICE</h2>
          <span className="alert-badge">{config.badge}</span>
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