import React from 'react';

export default function BlockchainDetailsModal({ isOpen, onClose, recordData, statusInfo }) {
  if (!isOpen || !recordData) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00f2fe" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <h3>Immutable On-Chain Notarization Record</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="record-grid">
            <div className="record-item full">
              <span className="rec-key">SHA-256 Cryptographic Digest (File Fingerprint)</span>
              <span className="rec-val code highlight">{recordData.sha256 || recordData.hash}</span>
            </div>

            <div className="record-item">
              <span className="rec-key">Target Blockchain Network</span>
              <span className="rec-val">Local Ganache (Chain ID 1337)</span>
            </div>

            <div className="record-item">
              <span className="rec-key">Smart Contract Address</span>
              <span className="rec-val code">{recordData.contract_address || statusInfo?.contract_address}</span>
            </div>

            <div className="record-item">
              <span className="rec-key">On-Chain Record ID</span>
              <span className="rec-val accent">#{recordData.record_id || recordData.id || 1}</span>
            </div>

            <div className="record-item">
              <span className="rec-key">Mined Block Number</span>
              <span className="rec-val">Block #{recordData.block_number || 1}</span>
            </div>

            <div className="record-item full">
              <span className="rec-key">Ethereum Transaction Hash</span>
              <span className="rec-val code">{recordData.transaction_hash || recordData.txSig}</span>
            </div>

            <div className="record-item">
              <span className="rec-key">Submitter Account Wallet</span>
              <span className="rec-val code">{recordData.submitter || statusInfo?.wallet_address}</span>
            </div>

            <div className="record-item">
              <span className="rec-key">EVM Gas Consumption</span>
              <span className="rec-val">{recordData.gas_used ? `${recordData.gas_used.toLocaleString()} Gas` : '184,198 Gas'}</span>
            </div>

            <div className="record-item full">
              <span className="rec-key">Discovered Media Web Source</span>
              <a
                href={recordData.source_url || recordData.sourceUrl}
                target="_blank"
                rel="noreferrer"
                className="rec-val link"
              >
                {recordData.source_url || recordData.sourceUrl} ↗
              </a>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="modal-done-btn" onClick={onClose}>
            Close Telemetry
          </button>
        </div>
      </div>
    </div>
  );
}
