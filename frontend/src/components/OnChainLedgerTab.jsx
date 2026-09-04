import React from 'react';

export default function OnChainLedgerTab({ onQuickVerify }) {
  const records = [
    {
      id: 1001,
      hash: "0xa7f28c11e3895a98d0f1...d1e43e2f",
      fullHash: "0xa7f28c11e3895a98d0f1982b6c934b071295b9c7fa689255627a9446d1e43e2f",
      sourceUrl: "https://images.unsplash.com/photo-tech-speaker",
      timestamp: "2026-09-04 22:15:30 UTC",
      submitter: "0x92aF...471C",
      fullSubmitter: "0x92aF0b5C52E461c210d321f92e10502a9041471C"
    },
    {
      id: 1002,
      hash: "0xb893c12988cb62804c86...8e291244",
      fullHash: "0xb893c12988cb62804c86125026b91129b860269389f417a80b8e291244e3b1c9",
      sourceUrl: "https://wikimedia.org/wiki/File:Portrait_Case.jpg",
      timestamp: "2026-09-04 21:50:12 UTC",
      submitter: "0x92aF...471C",
      fullSubmitter: "0x92aF0b5C52E461c210d321f92e10502a9041471C"
    }
  ];

  const exportJSON = () => {
    const data = records.map(r => ({
      record_id: r.id,
      hash: r.fullHash,
      source_url: r.sourceUrl,
      timestamp: r.timestamp,
      submitter: r.fullSubmitter,
      network: "Solana Devnet / Ethereum Sepolia"
    }));

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'hacker_house_ledger_records.json';
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
          On-Chain Notarization Ledger
        </span>
        <button
          className="nav-tag"
          onClick={exportJSON}
          style={{ cursor: 'pointer', background: 'transparent' }}
        >
          Download JSON Ledger
        </button>
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
