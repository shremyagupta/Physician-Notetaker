import React from 'react';

function Header() {

  return (
    <header className="app-header glass-panel">
      <div className="logo-container">
        <div className="logo-icon">⚕️</div>
        <h1 className="logo-text">Physician Notetaker</h1>
      </div>

      <div className="header-actions">
        <div className="status-badge">
          <span className="dot pulse"></span>
          Live Session
        </div>
      </div>

      <style>{`
        .app-header {
          height: 70px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 2rem;
          margin-bottom: 1.5rem;
          border-radius: 0 0 16px 16px;
          border-top: none;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .upload-btn {
          padding: 0.4rem 1rem;
          font-size: 0.85rem;
          border-color: rgba(255, 255, 255, 0.2);
        }

        .logo-container {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .logo-icon {
          font-size: 1.8rem;
          filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.5));
        }

        .logo-text {
          font-size: 1.4rem;
          background: linear-gradient(to right, #fff, #94a3b8);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.4rem 1rem;
          background: rgba(16, 185, 129, 0.1);
          border: 1px solid rgba(16, 185, 129, 0.3);
          border-radius: 20px;
          font-size: 0.85rem;
          color: var(--secondary);
          font-weight: 500;
        }

        .dot {
          width: 8px;
          height: 8px;
          background-color: var(--secondary);
          border-radius: 50%;
        }

        .pulse {
          animation: pulse-animation 2s infinite;
        }

        @keyframes pulse-animation {
          0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
          70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
          100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
      `}</style>
    </header>
  );
}

export default Header;
