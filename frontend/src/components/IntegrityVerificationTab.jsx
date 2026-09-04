import React, { useState } from 'react';

export default function IntegrityVerificationTab() {
  const [selectedFile, setSelectedFile] = useState('authentic');
  const [recordId, setRecordId] = useState('1');
  const [auditResult, setAuditResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const runAudit = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          record_id: parseInt(recordId, 10) || 1,
          file_type: selectedFile
        })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        setErrorMsg(data.error || 'Verification query failed on Ganache.');
        setAuditResult(null);
      } else {
        setAuditResult({
          isTampered: !data.is_match,
          local: data.local_hash,
          onChain: data.blockchain_hash,
          timestamp: data.timestamp,
          recordId: data.record_id,
          sourceUrl: data.source_url,
          contractAddress: data.contract_address,
          submitter: data.submitter
        });
      }
    } catch (err) {
      setErrorMsg(`Connection error: ${err.message}`);
    } finally {
      setLoading(false);
    }
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
        <span className="nav-tag">Ganache Smart Contract</span>
      </div>

      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>
        Re-hashes local media bytes in real-time and queries the immutable on-chain record on Local Ganache to mathematically prove authenticity.
      </p>

      <div className="form-group-row">
        <div className="form-control-block">
          <label className="control-title">Select Local File</label>
          <select
            className="ui-select"
            value={selectedFile}
            onChange={(e) => setSelectedFile(e.target.value)}
          >
            <option value="authentic">Authentic Content (output/matched_image.jpg)</option>
            <option value="tampered">Tampered Simulation (Modified Bytes)</option>
          </select>
        </div>
        <div className="form-control-block">
          <label className="control-title">On-Chain Record ID</label>
          <input
            type="number"
            className="ui-input"
            value={recordId}
            min="1"
            onChange={(e) => setRecordId(e.target.value)}
          />
        </div>
      </div>

      <button className="btn-action-primary" onClick={runAudit} disabled={loading}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <span>{loading ? 'Auditing Against Blockchain...' : 'Re-Hash & Audit Against Blockchain'}</span>
      </button>

      {errorMsg && (
        <div className="status-verdict-box tampered" style={{ marginTop: '16px' }}>
          <h4>Audit Query Failed</h4>
          <p>{errorMsg}</p>
        </div>
      )}

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
