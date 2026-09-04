import React from 'react';

export default function TopNavbar({ statusInfo }) {
  return (
    <header className="top-navbar">
      <div className="nav-brand-group">
        <div className="brand-icon-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
          </svg>
        </div>
        <div className="brand-title-wrap">
          <span className="brand-name">Hacker House</span>
          <span className="badge-goa-mini">गोवा</span>
        </div>
        <span className="nav-tag">Task 3: Production Pipeline</span>
      </div>

      <div className="nav-controls">
        <div className="system-status-pill">
          {statusInfo?.connected ? 'Ganache Online' : 'Connecting Ganache...'}
        </div>
        <div className="btn-network-select" style={{ cursor: 'default' }}>
          <span
            className="network-indicator-dot"
            style={{ background: statusInfo?.connected ? 'var(--status-verified)' : 'var(--status-tampered)' }}
          ></span>
          <span>
            {statusInfo?.connected
              ? `Local Ganache • Block #${statusInfo?.latest_block ?? 2}`
              : 'Local Ganache (Offline)'}
          </span>
        </div>
      </div>
    </header>
  );
}
