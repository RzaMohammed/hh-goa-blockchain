import React, { useState, useEffect } from 'react';

export default function HistoryView({ onSelectRecordForVerify }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchLedger = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/ledger');
      const data = await res.json();
      if (data.records) setRecords(data.records);
    } catch (e) {
      console.warn('Failed to fetch history:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLedger();
  }, []);

  return (
    <div className="history-view-panel">
      <div className="view-title-bar flex-between">
        <div>
          <h2>On-Chain Notarization History</h2>
          <p>Immutable cryptographic records recorded on the local Ganache blockchain.</p>
        </div>
        <button className="secondary-action-btn small" onClick={fetchLedger}>
          {loading ? 'Refreshing...' : '↻ Refresh Ledger'}
        </button>
      </div>

      {records.length === 0 ? (
        <div className="empty-history-box">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          <p>No on-chain records mined yet. Run a face verification search to create a record.</p>
        </div>
      ) : (
        <div className="history-cards-deck">
          {records.map((rec) => (
            <div key={rec.id} className="history-record-card">
              <div className="card-top">
                <span className="record-badge">RECORD #{rec.id}</span>
                <span className="record-time">{rec.timestamp}</span>
              </div>

              <div className="card-mid">
                <div className="rec-row">
                  <span className="lbl">SHA-256 Digest:</span>
                  <span className="val code">{rec.fullHash || rec.hash}</span>
                </div>
                <div className="rec-row">
                  <span className="lbl">Source URL:</span>
                  <a href={rec.sourceUrl} target="_blank" rel="noreferrer" className="val link">
                    {rec.sourceUrl} ↗
                  </a>
                </div>
                <div className="rec-row">
                  <span className="lbl">Submitter Account:</span>
                  <span className="val code muted">{rec.submitter || rec.fullSubmitter}</span>
                </div>
              </div>

              <div className="card-bottom">
                <button
                  className="primary-action-btn small border-only"
                  onClick={() => onSelectRecordForVerify(rec.id)}
                >
                  CHECK INTEGRITY ↗
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
