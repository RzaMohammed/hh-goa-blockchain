import React, { useState } from 'react';
import { ASSETS } from '../assets/datasets';

export default function TamperAuditLabTab() {
  const origHash = "a7f28c11e3895a98d0f1982b6c934b071295b9c7fa689255627a9446d1e43e2f";
  const mutatedHash = "3d99e526c7104b281f62b78b88df14299b8214fa39062dc962ceb33d0e2c8841";

  const [isTampered, setIsTampered] = useState(true);

  const injectTamper = () => {
    setIsTampered(true);
    alert('1-Byte Header Tamper Injected. Due to the Avalanche Effect, the entire SHA-256 digest completely mutated!');
  };

  const resetTamper = () => {
    setIsTampered(false);
    alert('Reset to authentic file buffer.');
  };

  return (
    <div className="console-panel" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div className="panel-header-row">
        <span className="panel-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          Avalanche Effect Demonstration
        </span>
        <span className="nav-tag" style={{ color: 'var(--status-tampered)' }}>
          Tamper Audit
        </span>
      </div>

      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.6', marginBottom: '16px' }}>
        Demonstrates how subtle changes break cryptographic integrity: modifying a single metadata byte alters the SHA-256 digest completely, triggering instant tamper detection.
      </p>

      <div className="diff-two-col">
        <div className="diff-panel">
          <div className="diff-title" style={{ color: 'var(--status-verified)' }}>AUTHENTIC LOCAL FILE</div>
          <div
            style={{
              height: '160px',
              background: '#0b1510',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '10px'
            }}
          >
            <img
              src={ASSETS.person}
              style={{ maxHeight: '100%', borderRadius: 'var(--radius-sm)' }}
              alt="Original"
            />
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>SHA-256 Digest:</div>
          <div className="diff-box" style={{ color: 'var(--status-verified)' }}>
            {origHash}
          </div>
        </div>

        <div className="diff-panel">
          <div className="diff-title" style={{ color: 'var(--status-tampered)' }}>ALTERED / TAMPERED FILE</div>
          <div
            style={{
              height: '160px',
              background: '#0b1510',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '10px',
              position: 'relative'
            }}
          >
            <img
              src={isTampered ? ASSETS.tamper : ASSETS.person}
              style={{
                maxHeight: '100%',
                borderRadius: 'var(--radius-sm)',
                filter: isTampered ? 'contrast(1.1) hue-rotate(15deg)' : 'none'
              }}
              alt="Tampered"
            />
            {isTampered && (
              <span className="nav-tag" style={{ position: 'absolute', top: '8px', right: '8px', color: 'var(--status-tampered)' }}>
                Modified
              </span>
            )}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
            {isTampered ? 'Mutated SHA-256 Digest:' : 'Current SHA-256 Digest:'}
          </div>
          <div
            className="diff-box"
            style={{ color: isTampered ? 'var(--status-tampered)' : 'var(--status-verified)' }}
          >
            {isTampered ? mutatedHash : origHash}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
        <button
          className="btn-action-primary"
          onClick={injectTamper}
          style={{ background: 'var(--status-tampered)', color: '#fff' }}
        >
          <span>Inject 1-Byte Modification & Recalculate</span>
        </button>
        <button className="btn-network-select" onClick={resetTamper}>
          <span>Reset to Authentic</span>
        </button>
      </div>
    </div>
  );
}
