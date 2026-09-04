import React, { useState, useEffect } from 'react';

export default function OnChainLedgerTab({ onQuickVerify }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchLedger = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/ledger');
      const data = await res.json();
      if (data.records && data.records.length > 0) {
        setRecords(data.records);
      } else {
        setRecords([]);
      }
    } catch (e) {
      console.warn('Failed to fetch ledger:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLedger();
  }, []);

  const exportJSON = () => {
    const data = records.map(r => ({
      record_id: r.id,
      hash: r.fullHash,
      source_url: r.sourceUrl,
      timestamp: r.timestamp,
      submitter: r.fullSubmitter,
      network: "Local Ganache (Chain ID 1337)"
    }));

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ganache_ledger_records.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="console-panel">
      <div className="panel-header-row">
        <span className="panel-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          On-Chain Notarization Ledger (Ganache)
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className="nav-tag"
            onClick={fetchLedger}
            style={{ cursor: 'pointer', background: 'transparent' }}
          >
            {loading ? 'Refreshing...' : '↻ Refresh Ledger'}
          </button>
          <button
            className="nav-tag"
            onClick={exportJSON}
            style={{ cursor: 'pointer', background: 'transparent' }}
          >
            Download JSON Ledger
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Record ID</th>
              <th>SHA-256 Digest</th>
              <th>Discovered Source URL</th>
              <th>Block Timestamp</th>
              <th>Submitter</th>
              <th>Verification</th>
            </tr>
          </thead>
          <tbody>
            {records.map(rec => (
              <tr key={rec.id}>
                <td style={{ color: 'var(--accent-yellow-text)', fontWeight: 700 }}>
                  #{rec.id}
                </td>
                <td>{rec.hash}</td>
                <td>{rec.sourceUrl}</td>
                <td>{rec.timestamp}</td>
                <td>{rec.submitter}</td>
                <td>
                  <button
                    className="nav-tag"
                    onClick={() => onQuickVerify(rec.id)}
                    style={{ cursor: 'pointer' }}
                  >
                    Verify
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
