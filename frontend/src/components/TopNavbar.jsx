import React from 'react';

export default function TopNavbar({ activeNetwork, toggleNetwork }) {
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
        <div className="system-status-pill">System Operational</div>
        <button className="btn-network-select" id="networkToggleBtn" onClick={toggleNetwork}>
          <span className="network-indicator-dot"></span>
          <span>{activeNetwork === 'solana' ? 'Solana Devnet (SPL Memo)' : 'Ethereum Sepolia (Solidity)'}</span>
        </button>
      </div>
    </header>
  );
}
