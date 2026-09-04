import React from 'react';

export default function ProjectHeader() {
  return (
    <section className="project-header-card">
      <div className="project-meta-row">
        <span className="project-location">Goa, India • October 28–31, 2026</span>
        <span className="project-studio">2:41 PM Studio</span>
      </div>

      <div className="project-title-row">
        <h1 className="project-title">Biometric Face Identification & On-Chain Ledger</h1>
      </div>

      <p className="project-desc">
        End-to-end media verification engine: extracts 512-d deep metric embeddings from input portraits, queries Google Lens reverse-image index, evaluates cosine similarity, computes RFC 8785 / SHA-256 digests, and notarizes immutable proofs on-chain.
      </p>

      <div className="tech-spec-bar">
        <div className="spec-chip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <span>OpenCV YuNet + SFace (512-d)</span>
        </div>
        <div className="spec-chip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <span>SerpApi Reverse Search</span>
        </div>
        <div className="spec-chip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
          <span>RFC 8785 Canonical SHA-256</span>
        </div>
        <div className="spec-chip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/></svg>
          <span>Solana Memo v2 / Sepolia Solidity</span>
        </div>
      </div>
    </section>
  );
}
