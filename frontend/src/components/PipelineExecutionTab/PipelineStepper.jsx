import React from 'react';
import { ASSETS } from '../../assets/datasets';

export default function PipelineStepper({
  steps,
  telemetryStatus,
  verdict,
  candidates,
  receipt,
  activeNetwork
}) {
  return (
    <div className="console-panel">
      <div className="panel-header-row">
        <span className="panel-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          Pipeline Telemetry & Notarization
        </span>
        <span
          className="nav-tag"
          style={{
            color:
              telemetryStatus === 'Running...'
                ? 'var(--accent-yellow-text)'
                : telemetryStatus === 'Notarized & Verified'
                ? 'var(--status-verified)'
                : telemetryStatus === 'Tamper Detected' || telemetryStatus === 'Halted'
                ? 'var(--status-tampered)'
                : telemetryStatus === 'Rejected'
                ? 'var(--status-lowmatch)'
                : 'var(--text-muted)'
          }}
        >
          {telemetryStatus}
        </span>
      </div>

      {/* Stepper List */}
      <div className="stepper-list">
        {steps.map(step => (
          <div
            key={step.id}
            className={`stepper-row ${step.state === 'active' ? 'active' : ''} ${
              step.state === 'completed' ? 'completed' : ''
            }`}
            style={{
              borderColor: step.state === 'failed' ? 'var(--status-tampered-border)' : undefined
            }}
          >
            <div className="step-index-badge">{step.id}</div>
            <div className="step-text-wrap">
              <div className="step-main-title">
                <span>{step.title}</span>
                <span className="step-meta-tag">{step.meta}</span>
              </div>
              <div className="step-sub-desc">{step.desc}</div>
            </div>
            <div
              className="step-state-badge"
              style={{
                color:
                  step.state === 'active'
                    ? 'var(--accent-yellow-text)'
                    : step.state === 'completed'
                    ? 'var(--status-verified)'
                    : step.state === 'failed'
                    ? 'var(--status-tampered)'
                    : 'var(--text-muted)'
              }}
            >
              {step.badge}
            </div>
          </div>
        ))}
      </div>

      {/* Verdict Outcome */}
      {verdict && (
        <div
          className={`status-verdict-box ${verdict.type}`}
          style={
            verdict.type === 'lowmatch'
              ? { background: 'var(--status-lowmatch-bg)', borderColor: 'var(--status-lowmatch-border)' }
              : verdict.type === 'noface'
              ? { background: 'var(--status-noface-bg)', borderColor: 'var(--status-noface-border)' }
              : undefined
          }
        >
          <h4
            style={{
              color:
                verdict.type === 'lowmatch'
                  ? 'var(--status-lowmatch)'
                  : verdict.type === 'noface'
                  ? 'var(--status-noface)'
                  : undefined
            }}
          >
            {verdict.title}
          </h4>
          <p>{verdict.message}</p>
        </div>
      )}

      {/* Discovered Candidates */}
      {candidates && candidates.length > 0 && (
        <div style={{ marginTop: '14px' }}>
          <div className="section-micro-label">Evaluated Candidates</div>
          <div className="candidates-deck">
            {candidates.map((cand, idx) => (
              <div
                key={idx}
                className={`candidate-entry ${cand.isBest ? 'best' : ''}`}
                style={{ opacity: cand.opacity || 1 }}
              >
                <img
                  src={cand.avatar || '/input/person.jpg'}
                  className="candidate-avatar"
                  alt={cand.label}
                  onError={(e) => { e.currentTarget.src = '/input/person.jpg'; }}
                />
                <div className="candidate-info-box">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px', flexWrap: 'wrap' }}>
                    <span className="candidate-label">{cand.label}</span>
                    {cand.platform && (
                      <span className={`platform-pill ${cand.platform}`}>
                        {cand.platform}
                      </span>
                    )}
                  </div>
                  <a
                    href={cand.link}
                    target="_blank"
                    rel="noreferrer"
                    className="candidate-link"
                    style={{ textDecoration: 'none', color: 'var(--text-secondary)' }}
                  >
                    {cand.link} ↗
                  </a>
                  <div className="metric-bar-group">
                    <div className="metric-track">
                      <div
                        className="metric-fill"
                        style={{
                          width: `${cand.score}%`,
                          background: cand.color || 'var(--status-verified)'
                        }}
                      />
                    </div>
                    <div
                      className="metric-score-label"
                      style={{ color: cand.color || 'var(--status-verified)' }}
                    >
                      {cand.score}%
                    </div>
                  </div>
                </div>
                <span className="nav-tag" style={{ color: cand.tagColor }}>
                  {cand.tag}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* On-Chain Proof Receipt */}
      {receipt && (
        <div className="receipt-container">
          <div className="receipt-header">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            On-Chain Transaction Receipt & Telemetry
          </div>
          <div className="receipt-data-row">
            <span className="receipt-key">Target Network:</span>
            <span className="receipt-val highlight">{receipt.network}</span>
          </div>
          <div className="receipt-data-row">
            <span className="receipt-key">Tx Signature:</span>
            <span className="receipt-val">{receipt.txSig}</span>
          </div>
          <div className="receipt-data-row">
            <span className="receipt-key">SHA-256 Digest:</span>
            <span className="receipt-val highlight">{receipt.sha256}</span>
          </div>
          <div className="receipt-data-row">
            <span className="receipt-key">Cosine Score:</span>
            <span className="receipt-val" style={{ color: 'var(--status-verified)' }}>
              {receipt.score}
            </span>
          </div>
          <div className="receipt-data-row">
            <span className="receipt-key">Tx Status / Slot:</span>
            <span className="receipt-val">{receipt.slotState}</span>
          </div>
          <div className="receipt-data-row">
            <span className="receipt-key">Total Latency:</span>
            <span className="receipt-val">{receipt.latency}</span>
          </div>
          <div className="receipt-data-row">
            <span className="receipt-key">Ledger Network:</span>
            <span className="receipt-val highlight">
              {receipt.network || 'Local Ganache (Chain ID 1337)'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
