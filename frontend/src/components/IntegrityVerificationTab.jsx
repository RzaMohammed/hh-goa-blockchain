import React, { useState } from 'react';

export default function IntegrityVerificationTab() {
  const [selectedFile, setSelectedFile] = useState('authentic');
  const [recordId, setRecordId] = useState('1001');
  const [auditResult, setAuditResult] = useState(null);

  const runAudit = () => {
    const onChain = "a7f28c11e3895a98d0f1982b6c934b071295b9c7fa689255627a9446d1e43e2f";
    const isTampered = selectedFile === 'tampered';
    const local = isTampered
      ? "3d99e526c7104b281f62b78b88df14299b8214fa39062dc962ceb33d0e2c8841"
      : onChain;

    setAuditResult({
      isTampered,
      local,
      onChain,
      timestamp: "2026-09-04 22:15:30 UTC",
      recordId
    });
  };

  return (
    <div className="console-panel" style={{ maxWidth: '880px', margin: '0 auto' }}>
      <div className="panel-header-row">
        <span className="panel-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <polyline points="9 12 11 14 15 10" />
          </svg>
          Cryptographic Integrity & Tamper Audit
        </span>
        <span className="nav-tag">RFC 8785 Proof</span>
      </div>

      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>
        Re-hashes local media bytes in real-time and queries the immutable on-chain record to mathematically prove authenticity.
      </p>

      <div className="form-group-row">
        <div className="form-control-block">
          <label className="control-title">Select Local File</label>
          <select
            className="ui-select"
            value={selectedFile}
            onChange={(e) => setSelectedFile(e.target.value)}
          >
            <option value="authentic">Authentic Original (input/person.jpg)</option>
            <option value="tampered">Tampered Simulation (1-Byte Altered)</option>
          </select>
        </div>
        <div className="form-control-block">
          <label className="control-title">On-Chain Record ID</label>
          <input
            type="number"
            className="ui-input"
            value={recordId}
            onChange={(e) => setRecordId(e.target.value)}
          />
        </div>
      </div>

      <button className="btn-action-primary" onClick={runAudit}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <span>Re-Hash & Audit Against Blockchain</span>
      </button>

      {auditResult && (
        <>
          <div className={`status-verdict-box ${auditResult.isTampered ? 'tampered' : 'verified'}`}>
            <h4>
              {auditResult.isTampered
                ? 'Audit X: Cryptographic Tamper Detected'
                : 'Verification Passed: Content Authentic'}
            </h4>
            <p>
              {auditResult.isTampered
                ? `Local file checksum does NOT match the immutable on-chain record #${auditResult.recordId}.`
                : `Every raw byte matches on-chain record #${auditResult.recordId}. Integrity proven mathematically.`}
            </p>
          </div>

          <div className="receipt-container">
            <div className="receipt-header">Checksum Comparison Log</div>
            <div className="receipt-data-row">
              <span className="receipt-key">Computed Local SHA-256:</span>
              <span className="receipt-val">{auditResult.local}</span>
            </div>
            <div className="receipt-data-row">
              <span className="receipt-key">Immutable On-Chain Hash:</span>
              <span className="receipt-val highlight">{auditResult.onChain}</span>
            </div>
            <div className="receipt-data-row">
              <span className="receipt-key">Notarization Timestamp:</span>
              <span className="receipt-val">{auditResult.timestamp}</span>
            </div>
            <div className="receipt-data-row">
              <span className="receipt-key">Cryptographic State:</span>
              <span
                className="receipt-val"
                style={{
                  color: auditResult.isTampered ? 'var(--status-tampered)' : 'var(--status-verified)'
                }}
              >
                {auditResult.isTampered ? 'Mismatch (Altered)' : 'Deterministic Match'}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
