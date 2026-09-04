import React from 'react';

export default function ArchitectureSpecsTab() {
  const solidityCode = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FaceVerification {
    struct Record {
        bytes32 dataHash;
        string sourceUrl;
        uint256 timestamp;
        address submitter;
    }

    mapping(uint256 => Record) private records;
    mapping(bytes32 => uint256) private hashToRecordId;
    uint256 public recordCount;

    event DataRegistered(uint256 indexed recordId, bytes32 dataHash, string sourceUrl, uint256 timestamp, address indexed submitter);

    function registerRecord(bytes32 _dataHash, string calldata _sourceUrl) external returns (uint256) {
        require(_dataHash != bytes32(0), "Hash cannot be zero");
        recordCount++;
        records[recordCount] = Record(_dataHash, _sourceUrl, block.timestamp, msg.sender);
        hashToRecordId[_dataHash] = recordCount;
        emit DataRegistered(recordCount, _dataHash, _sourceUrl, block.timestamp, msg.sender);
        return recordCount;
    }

    function getRecord(uint256 _recordId) external view returns (bytes32, string memory, uint256, address) {
        Record memory rec = records[_recordId];
        require(rec.timestamp > 0, "Record does not exist");
        return (rec.dataHash, rec.sourceUrl, rec.timestamp, rec.submitter);
    }
}`;

  return (
    <div className="console-panel" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div className="panel-header-row">
        <span className="panel-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
          </svg>
          System Architecture & Solidity Specifications
        </span>
        <span className="nav-tag">Solidity ^0.8.20</span>
      </div>

      <div className="form-group-row" style={{ marginBottom: '16px' }}>
        <div>
          <h4 style={{ color: 'var(--accent-yellow-text)', fontSize: '0.85rem', marginBottom: '6px' }}>
            Gas Optimization: bytes32 Storage
          </h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            In Ethereum smart contract design, storing hashes as <code>bytes32</code> uses exactly 1 EVM word (32 bytes = 20,000 gas cold write). Dynamic <code>string</code> representations consume multiple words plus offset encoding (~40,000+ gas). Using <code>bytes32</code> cuts on-chain gas costs by over 45%.
          </p>
        </div>
        <div>
          <h4 style={{ color: 'var(--status-verified)', fontSize: '0.85rem', marginBottom: '6px' }}>
            Biometric Metric Invariance
          </h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            OpenCV YuNet extracts 5 fiducials (eyes, nose, mouth corners) to align the face to a canonical frame. SFace extracts a normalized 512-d feature vector on a unit hypersphere, ensuring Cosine Similarity is invariant to head pose and illumination.
          </p>
        </div>
      </div>

      <div
        style={{
          background: 'var(--bg-code)',
          border: '1px solid var(--border-subtle)',
          padding: '14px',
          borderRadius: 'var(--radius-md)',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.74rem',
          overflowX: 'auto',
          color: '#a7f3d0'
        }}
      >
        <pre>{solidityCode}</pre>
      </div>
    </div>
  );
}
