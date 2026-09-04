import React from 'react';

export default function BottomStatusDock({ activeNetwork, onOpenSpecs }) {
  return (
    <footer className="bottom-status-dock">
      <div className="dock-left">
        <div className="dock-item">
          <span className="dock-dot"></span>
          <span>{activeNetwork === 'solana' ? 'Solana Devnet' : 'Ethereum Sepolia'}</span>
        </div>
        <div className="dock-item">
          <span>Latency: <strong style={{ color: 'var(--text-primary)' }}>38ms</strong></span>
        </div>
        <div className="dock-item">
          <span>Slot: <strong style={{ color: 'var(--text-primary)' }}>#291,048,122</strong></span>
        </div>
        <div className="dock-item">
          <span>RFC 8785 Canonical v1</span>
        </div>
      </div>

      <div className="dock-right">
        <div className="dock-item">
          <span>OpenCV 4.10 (YuNet + SFace 512-d)</span>
        </div>
        <div className="dock-item">
          <span>Solidity ^0.8.20</span>
        </div>
        <button className="dock-link" onClick={onOpenSpecs}>
          Architecture Docs ↗
        </button>
      </div>
    </footer>
  );
}
