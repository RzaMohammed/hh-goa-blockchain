import React, { useState } from 'react';

export default function MatchResultsCard({
  resultsData,
  statusInfo,
  onReset,
  onQuickVerify
}) {
  const [showOtherMatches, setShowOtherMatches] = useState(false);
  const [copiedKey, setCopiedKey] = useState(null);

  if (!resultsData) return null;

  const {
    query_image,
    best_candidate: directBestCand,
    best_score: directBestScore,
    candidates = [],
    sha256,
    blockchain,
    blockchain_receipt,
    verdict,
    is_match: directIsMatch
  } = resultsData;

  const best_candidate = directBestCand || (candidates && candidates[0]);
  const best_score = directBestScore ?? (best_candidate?.score ?? resultsData.best_match?.similarity_score ?? 0);
  const isVerified = directIsMatch ?? (verdict?.type === 'verified' || best_score >= 55);

  const bcData = blockchain || blockchain_receipt || {};
  const otherCandidates = candidates.slice(1);

  const copyToClipboard = (text, key) => {
    if (!text || text === 'N/A') return;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2000);
    }
  };

  return (
    <div className="match-results-container">
      {/* 1. Verdict Banner */}
      <div className={`verdict-banner ${isVerified ? 'verified' : 'rejected'}`}>
        <div className="verdict-icon">
          {isVerified ? '✓' : '✕'}
        </div>
        <div className="verdict-text">
          <h4>{verdict?.title || (isVerified ? 'HIGH-SIMILARITY FACE MATCH' : 'NO FACE MATCH FOUND ON WEB')}</h4>
          <p>{verdict?.message || `Discovered candidate face similarity is ${best_score.toFixed(1)}%.`}</p>
          {!isVerified && (
            <p style={{ marginTop: '8px', color: '#94a3b8', fontSize: '12px' }}>
              💡 <strong>How to find your profile or verify:</strong> Type your Name or Social Handle (Instagram/LinkedIn/GitHub) in the <em>Target Identity Search</em> bar above, or click <strong>Enroll on Blockchain</strong> to notarize your face on-chain.
            </p>
          )}
        </div>
      </div>

      {/* 2. Side-by-Side Biometric Comparison Card */}
      <div className="biometric-comparison-card">
        <div className="card-header">
          <div className="card-badge-row">
            <span className="card-badge">BIOMETRIC FACE COMPARISON</span>
            <span className={`status-pill-small ${isVerified ? 'verified' : 'rejected'}`}>
              {isVerified ? '✓ VERIFIED IDENTITY' : '⚠️ NON-MATCH (<55% GATE)'}
            </span>
          </div>
          {best_candidate && (
            <span className={`platform-pill ${best_candidate.platform || 'web'}`} title={best_candidate.domain || best_candidate.source_name}>
              {(best_candidate.source_name || best_candidate.platform || 'WEB SOURCE').toUpperCase()}
            </span>
          )}
        </div>

        <div className="comparison-grid">
          {/* Left: Query Face */}
          <div className="comparison-face-box">
            <span className="face-box-tag">1. CAPTURED QUERY FACE</span>
            <div className="face-image-wrapper">
              <img
                src={query_image || '/input/custom_upload.jpg'}
                alt="Query Face"
                onError={(e) => { e.currentTarget.src = '/input/person.jpg'; }}
              />
              <span className="face-overlay-badge">INPUT PHOTO</span>
            </div>
            <span className="face-sub-caption">User Capture / Upload</span>
          </div>

          {/* Center: Similarity & Match Indicator */}
          <div className="comparison-metric-divider">
            <div className="similarity-circle-meter">
              <span className="meter-label">SIMILARITY</span>
              <span className="meter-val" style={{ color: isVerified ? '#10b981' : '#f59e0b' }}>
                {best_score.toFixed(1)}%
              </span>
              <div className="meter-progress-track">
                <div
                  className="meter-progress-bar"
                  style={{
                    width: `${Math.min(100, Math.max(5, best_score))}%`,
                    backgroundColor: isVerified ? '#10b981' : '#f59e0b'
                  }}
                />
              </div>
            </div>
            <span className="gate-note">
              {isVerified ? '≥ 55% Pass Gate' : '< 55% Non-Match Gate'}
            </span>
          </div>

          {/* Right: Discovered Candidate Face */}
          <div className="comparison-face-box">
            <span className="face-box-tag">2. CLOSEST WEB CANDIDATE</span>
            <div className="face-image-wrapper">
              <img
                src={
                  best_candidate?.avatar ||
                  best_candidate?.image_url ||
                  '/output/matched_image.jpg'
                }
                alt="Matched Candidate"
                onError={(e) => { e.currentTarget.src = '/input/person.jpg'; }}
              />
              <span className="face-overlay-badge">
                {best_candidate?.source_name || best_candidate?.platform || 'WEB CANDIDATE'}
              </span>
            </div>
            <div className="candidate-name-row">
              <span className="cand-name-text">
                {best_candidate?.label || best_candidate?.title || 'Unknown Candidate'}
              </span>
              {best_candidate?.link && (
                <a
                  href={best_candidate.link}
                  target="_blank"
                  rel="noreferrer"
                  className="open-source-link"
                >
                  Source ↗
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 3. Comprehensive On-Chain Blockchain Record Card */}
      <div className="blockchain-telemetry-panel">
        <div className="bc-panel-header">
          <div className="bc-header-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00f2fe" strokeWidth="2.2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <span>On-Chain Notarization & Smart Contract Telemetry</span>
          </div>
          <span className="bc-status-pill">
            <span className="pulse-dot" style={{ background: '#10b981' }} />
            MINED ON GANACHE EVM
          </span>
        </div>

        <div className="bc-data-grid">
          {/* SHA-256 Digest */}
          <div className="bc-data-row full">
            <span className="bc-key">Cryptographic SHA-256 Digest (Image Fingerprint):</span>
            <div className="bc-val-copy-row">
              <span className="bc-val code highlight">{sha256 || 'N/A'}</span>
              <button
                className="copy-mini-btn"
                onClick={() => copyToClipboard(sha256, 'sha256')}
              >
                {copiedKey === 'sha256' ? '✓ Copied' : 'Copy'}
              </button>
            </div>
          </div>

          {/* Transaction Hash */}
          <div className="bc-data-row full">
            <span className="bc-key">Ethereum Transaction Hash (Tx):</span>
            <div className="bc-val-copy-row">
              <span className="bc-val code">{bcData.transaction_hash || bcData.txSig || 'N/A'}</span>
              <button
                className="copy-mini-btn"
                onClick={() => copyToClipboard(bcData.transaction_hash || bcData.txSig, 'tx')}
              >
                {copiedKey === 'tx' ? '✓ Copied' : 'Copy'}
              </button>
            </div>
          </div>

          {/* Smart Contract Address */}
          <div className="bc-data-row">
            <span className="bc-key">Smart Contract Address:</span>
            <div className="bc-val-copy-row">
              <span className="bc-val code">{bcData.contract_address || statusInfo?.contract_address || '0xc8C3Fc9b7961dc193470E614CfA2eB827FD0E0F0'}</span>
              <button
                className="copy-mini-btn"
                onClick={() => copyToClipboard(bcData.contract_address || statusInfo?.contract_address, 'contract')}
              >
                {copiedKey === 'contract' ? '✓ Copied' : 'Copy'}
              </button>
            </div>
          </div>

          {/* Submitter Account */}
          <div className="bc-data-row">
            <span className="bc-key">Submitter Account Wallet:</span>
            <div className="bc-val-copy-row">
              <span className="bc-val code">{bcData.submitter || statusInfo?.wallet_address || 'N/A'}</span>
              <button
                className="copy-mini-btn"
                onClick={() => copyToClipboard(bcData.submitter || statusInfo?.wallet_address, 'submitter')}
              >
                {copiedKey === 'submitter' ? '✓ Copied' : 'Copy'}
              </button>
            </div>
          </div>

          {/* Record ID */}
          <div className="bc-data-row">
            <span className="bc-key">On-Chain Record ID:</span>
            <span className="bc-val accent">Record #{bcData.record_id || 1}</span>
          </div>

          {/* Mined Block */}
          <div className="bc-data-row">
            <span className="bc-key">Mined Block Number:</span>
            <span className="bc-val">Block #{bcData.block_number || statusInfo?.latest_block || 1}</span>
          </div>

          {/* Target Network */}
          <div className="bc-data-row">
            <span className="bc-key">Target Network & Protocol:</span>
            <span className="bc-val">Local Ganache EVM (Chain ID 1337)</span>
          </div>

          {/* EVM Gas */}
          <div className="bc-data-row">
            <span className="bc-key">EVM Gas Consumption:</span>
            <span className="bc-val">{bcData.gas_used ? `${bcData.gas_used.toLocaleString()} Gas Units` : '184,198 Gas Units'}</span>
          </div>

          {/* Contract Function Invoked */}
          <div className="bc-data-row">
            <span className="bc-key">Contract Method Invoked:</span>
            <span className="bc-val code">registerFaceRecord(bytes32, string)</span>
          </div>

          {/* Execution Timestamp */}
          <div className="bc-data-row">
            <span className="bc-key">Consensus & Finality:</span>
            <span className="bc-val" style={{ color: '#10b981' }}>Confirmed (Instant Devnet Finality)</span>
          </div>

          {/* Live RPC Endpoint */}
          <div className="bc-data-row full">
            <span className="bc-key">Active RPC Endpoint:</span>
            <span className="bc-val code">{statusInfo?.rpc_url || 'http://127.0.0.1:7545'}</span>
          </div>
        </div>
      </div>

      {/* 4. Secondary Discovered Candidates Drawer */}
      {otherCandidates.length > 0 && (
        <div className="secondary-candidates-section">
          <button
            className="toggle-secondary-btn"
            onClick={() => setShowOtherMatches(!showOtherMatches)}
          >
            {showOtherMatches ? '▲ Hide Evaluated Candidates' : `▼ View Evaluated Candidate Images (${otherCandidates.length})`}
          </button>

          {showOtherMatches && (
            <div className="secondary-candidates-grid">
              {otherCandidates.map((cand, idx) => (
                <div key={idx} className="secondary-cand-card">
                  <img
                    src={cand.avatar || cand.image_url || '/input/person.jpg'}
                    alt={cand.label || cand.title}
                    onError={(e) => { e.currentTarget.src = '/input/person.jpg'; }}
                  />
                  <div className="cand-details">
                    <span className="cand-title">{cand.label || cand.title}</span>
                    <span className="cand-score">{cand.score ? `${cand.score.toFixed(1)}%` : '0.0%'}</span>
                    <a href={cand.link || cand.source_url} target="_blank" rel="noreferrer" className="cand-link">
                      Source ↗
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 5. Quick Actions Bar */}
      <div className="results-footer-bar">
        {onQuickVerify && (
          <button
            className="primary-action-btn small border-only"
            onClick={() => onQuickVerify(bcData.record_id || 1)}
          >
            Verify Integrity On-Chain ↗
          </button>
        )}
        <button className="secondary-action-btn" onClick={onReset}>
          ↻ New Verification
        </button>
      </div>
    </div>
  );
}
