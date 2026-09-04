import React from 'react';

export default function BottomStatusDock({ statusInfo, onOpenSpecs }) {
  const shortAddr = statusInfo?.contract_address
    ? `${statusInfo.contract_address.slice(0, 6)}...${statusInfo.contract_address.slice(-4)}`
    : '0x38B0...4a02';

  return (
    <footer className="bottom-status-dock">
      <div className="dock-left">
        <div className="dock-item">
          <span
            className="dock-dot"
            style={{ background: statusInfo?.connected ? 'var(--status-verified)' : 'var(--status-tampered)' }}
          ></span>
          <span>Local Ganache (Chain ID 1337)</span>
        </div>
        <div className="dock-item">
          <span>Block: <strong style={{ color: 'var(--text-primary)' }}>#{statusInfo?.latest_block ?? 2}</strong></span>
        </div>
        <div className="dock-item">
          <span>Contract: <strong style={{ color: 'var(--text-primary)' }}>{shortAddr}</strong></span>
        </div>
        <div className="dock-item">
          <span>Records: <strong style={{ color: 'var(--text-primary)' }}>{statusInfo?.total_records ?? 1}</strong></span>
        </div>
        <div className="dock-item">
          <span>Balance: <strong style={{ color: 'var(--text-primary)' }}>{statusInfo?.wallet_balance ?? 99.9} ETH</strong></span>
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
