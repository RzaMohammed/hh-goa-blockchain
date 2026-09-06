import React, { useState, useRef, useCallback } from 'react';

export default function VerificationView({ statusInfo }) {
  const [recordId, setRecordId] = useState('1');
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [tamperStatus, setTamperStatus] = useState(null);

  // Photo Upload Verification State
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadPreview, setUploadPreview] = useState(null);
  const [uploadVerifying, setUploadVerifying] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleVerify = async () => {
    setVerifying(true);
    setVerificationResult(null);
    try {
      const res = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ record_id: parseInt(recordId, 10) })
      });
      const data = await res.json();
      setVerificationResult(data);
    } catch (err) {
      setVerificationResult({
        success: false,
        error: `Verification failed: ${err.message}`
      });
    } finally {
      setVerifying(false);
    }
  };

  const handleTamperAction = async (action) => {
    try {
      const res = await fetch('/api/tamper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      const data = await res.json();
      setTamperStatus(data);
      // Auto re-verify to show live pass/fail transition
      handleVerify();
    } catch (err) {
      console.warn('Tamper action error:', err);
    }
  };

  // ----- Photo Upload Handlers -----
  const processFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setUploadedFile(file);
    setUploadResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadPreview(e.target.result);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) processFile(file);
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, [processFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleUploadVerify = async () => {
    if (!uploadPreview) return;
    setUploadVerifying(true);
    setUploadResult(null);

    try {
      const res = await fetch('/api/verify-upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: uploadPreview })
      });
      const data = await res.json();
      setUploadResult(data);
    } catch (err) {
      setUploadResult({
        success: false,
        error: `Upload verification failed: ${err.message}`
      });
    } finally {
      setUploadVerifying(false);
    }
  };

  const handleClearUpload = () => {
    setUploadedFile(null);
    setUploadPreview(null);
    setUploadResult(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="verification-view-panel">
      <div className="view-title-bar">
        <h2>Content Integrity Verification</h2>
        <p>Mathematically prove whether local media has been altered using on-chain SHA-256 digests.</p>
      </div>

      {/* ============================================================ */}
      {/* PHOTO UPLOAD VERIFICATION SECTION */}
      {/* ============================================================ */}
      <div className="upload-verify-section">
        <div className="upload-verify-header">
          <div className="upload-verify-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <div>
            <h3>Upload Photo &amp; Check Blockchain</h3>
            <p>Upload any photo to hash it and instantly check if it already exists on the blockchain.</p>
          </div>
        </div>

        <div className="upload-verify-body">
          {/* Drop Zone */}
          <div
            className={`upload-dropzone ${isDragOver ? 'drag-over' : ''} ${uploadPreview ? 'has-file' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => !uploadPreview && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />

            {uploadPreview ? (
              <div className="upload-preview-container">
                <img src={uploadPreview} alt="Uploaded preview" className="upload-preview-img" />
                <div className="upload-preview-info">
                  <span className="upload-filename">{uploadedFile?.name}</span>
                  <span className="upload-filesize">
                    {uploadedFile ? `${(uploadedFile.size / 1024).toFixed(1)} KB` : ''}
                  </span>
                </div>
                <button className="upload-clear-btn" onClick={(e) => { e.stopPropagation(); handleClearUpload(); }}>
                  ✕ Remove
                </button>
              </div>
            ) : (
              <div className="upload-placeholder">
                <div className="upload-placeholder-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                </div>
                <p className="upload-placeholder-text">
                  Drag &amp; drop a photo here, or <span className="upload-browse-link">browse files</span>
                </p>
                <p className="upload-placeholder-hint">Supports JPG, PNG, WEBP, BMP</p>
              </div>
            )}
          </div>

          {/* Verify Button */}
          {uploadPreview && (
            <button
              className="primary-action-btn upload-verify-btn"
              onClick={handleUploadVerify}
              disabled={uploadVerifying}
            >
              {uploadVerifying ? (
                <>
                  <span className="btn-spinner" />
                  HASHING &amp; SCANNING BLOCKCHAIN...
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                  HASH PHOTO &amp; SEARCH BLOCKCHAIN
                </>
              )}
            </button>
          )}

          {/* Upload Verification Result */}
          {uploadResult && (
            <div className="upload-result-container">
              {uploadResult.success ? (
                <>
                  {uploadResult.exists_on_chain ? (
                    <div className="outcome-banner pass upload-outcome">
                      <div className="outcome-icon">✓</div>
                      <div className="outcome-text">
                        {uploadResult.matched_record?.match_type === 'BIOMETRIC_FACE' ? (
                          <>
                            <h3>BIOMETRIC FACE MATCH FOUND ON BLOCKCHAIN</h3>
                            <p>
                              Biometrically matches enrolled on-chain identity <strong>{uploadResult.matched_record.name || 'Verified Subject'}</strong> with{' '}
                              <strong style={{ color: '#10b981' }}>{uploadResult.matched_record.similarity_percentage}% similarity</strong>! (Record #{uploadResult.matched_record.record_id})
                            </p>
                          </>
                        ) : (
                          <>
                            <h3>EXACT HASH FOUND ON BLOCKCHAIN</h3>
                            <p>This exact photo was previously registered on-chain. Its SHA-256 fingerprint matches record #{uploadResult.matched_record?.record_id}.</p>
                          </>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="outcome-banner not-found upload-outcome">
                      <div className="outcome-icon">✕</div>
                      <div className="outcome-text">
                        <h3>NOT FOUND ON BLOCKCHAIN</h3>
                        <p>
                          No on-chain record matches this photo's fingerprint or biometric face template.
                          {uploadResult.total_records_scanned > 0
                            ? ` Scanned ${uploadResult.total_records_scanned} record(s).`
                            : ' No records exist on the blockchain yet.'}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="hash-comparison-box upload-hash-box">
                    <div className="hash-row">
                      <span className="hash-label">Uploaded Photo SHA-256:</span>
                      <span className="hash-val code highlight">{uploadResult.uploaded_hash}</span>
                    </div>
                    {uploadResult.matched_record?.match_type === 'BIOMETRIC_FACE' && (
                      <>
                        <div className="hash-row">
                          <span className="hash-label">Biometric Verification:</span>
                          <span className="hash-val" style={{ color: '#10b981', fontWeight: 700 }}>
                            {uploadResult.matched_record.similarity_percentage}% Biometric Match
                          </span>
                        </div>
                        <div className="hash-row">
                          <span className="hash-label">Enrolled Identity:</span>
                          <span className="hash-val accent" style={{ fontWeight: 600 }}>
                            {uploadResult.matched_record.name}
                          </span>
                        </div>
                      </>
                    )}
                    <div className="hash-row">
                      <span className="hash-label">Records Scanned:</span>
                      <span className="hash-val">{uploadResult.total_records_scanned || 0}</span>
                    </div>
                    <div className="hash-row">
                      <span className="hash-label">Smart Contract:</span>
                      <span className="hash-val code">{uploadResult.contract_address || 'N/A'}</span>
                    </div>

                    {uploadResult.matched_record && (
                      <>
                        <div className="hash-divider" />
                        <div className="hash-row">
                          <span className="hash-label">Matched Record ID:</span>
                          <span className="hash-val accent">#{uploadResult.matched_record.record_id}</span>
                        </div>
                        <div className="hash-row">
                          <span className="hash-label">On-Chain Hash:</span>
                          <span className="hash-val code">{uploadResult.matched_record.blockchain_hash}</span>
                        </div>
                        <div className="hash-row">
                          <span className="hash-label">Source URL:</span>
                          <span className="hash-val code">{uploadResult.matched_record.source_url}</span>
                        </div>
                        <div className="hash-row">
                          <span className="hash-label">Notarized Timestamp:</span>
                          <span className="hash-val">{uploadResult.matched_record.timestamp}</span>
                        </div>
                        {uploadResult.matched_record.submitter && (
                          <div className="hash-row">
                            <span className="hash-label">Submitter Wallet:</span>
                            <span className="hash-val code">{uploadResult.matched_record.submitter}</span>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </>
              ) : (
                <div className="outcome-banner fail upload-outcome">
                  <div className="outcome-icon">⚠</div>
                  <div className="outcome-text">
                    <h3>VERIFICATION ERROR</h3>
                    <p>{uploadResult.error || 'An unexpected error occurred.'}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ============================================================ */}
      {/* EXISTING: RECORD ID VERIFICATION */}
      {/* ============================================================ */}
      <div className="verify-card-box">
        <div className="verify-section-divider">
          <span>OR VERIFY BY RECORD ID</span>
        </div>

        <div className="verify-controls-row">
          <div className="input-group">
            <label>On-Chain Record ID:</label>
            <input
              type="number"
              value={recordId}
              onChange={(e) => setRecordId(e.target.value)}
              className="rec-id-input"
              min="1"
            />
          </div>

          <button className="primary-action-btn small" onClick={handleVerify} disabled={verifying}>
            {verifying ? 'VERIFYING...' : 'CHECK ON-CHAIN INTEGRITY'}
          </button>
        </div>

        {/* Verification Result Card */}
        {verificationResult && (
          <div className="verification-outcome-container">
            {verificationResult.success && verificationResult.is_match ? (
              <div className="outcome-banner pass">
                <div className="outcome-icon">✓</div>
                <div className="outcome-text">
                  <h3>VERIFIED</h3>
                  <p>The current file matches the fingerprint recorded on the local Ganache blockchain.</p>
                </div>
              </div>
            ) : (
              <div className="outcome-banner fail">
                <div className="outcome-icon">✕</div>
                <div className="outcome-text">
                  <h3>VERIFICATION FAILED</h3>
                  <p>CONTENT MODIFIED — The current file differs from the recorded version on-chain.</p>
                </div>
              </div>
            )}

            <div className="hash-comparison-box">
              <div className="hash-row">
                <span className="hash-label">Original Fingerprint (On-Chain):</span>
                <span className="hash-val code highlight">
                  {verificationResult.blockchain_hash || verificationResult.record?.hash || 'N/A'}
                </span>
              </div>
              <div className="hash-row">
                <span className="hash-label">Current File Fingerprint:</span>
                <span
                  className="hash-val code"
                  style={{
                    color: verificationResult.is_match ? '#10b981' : '#ef4444'
                  }}
                >
                  {verificationResult.local_hash || 'N/A'}
                </span>
              </div>
              <div className="hash-row">
                <span className="hash-label">Smart Contract Address:</span>
                <span className="hash-val code">
                  {verificationResult.contract_address || statusInfo?.contract_address || '0xc8C3Fc9b7961dc193470E614CfA2eB827FD0E0F0'}
                </span>
              </div>
              <div className="hash-row">
                <span className="hash-label">Submitter Wallet Account:</span>
                <span className="hash-val code">
                  {verificationResult.submitter || statusInfo?.wallet_address || 'N/A'}
                </span>
              </div>
              <div className="hash-row">
                <span className="hash-label">Blockchain Notarized Time:</span>
                <span className="hash-val">
                  {verificationResult.timestamp || 'N/A'}
                </span>
              </div>
              <div className="hash-row">
                <span className="hash-label">Notarized Source Origin:</span>
                <span className="hash-val code">
                  {verificationResult.source_url || 'N/A'}
                </span>
              </div>
              <div className="hash-row">
                <span className="hash-label">Target Network & Protocol:</span>
                <span className="hash-val">
                  Local Ganache EVM (Chain ID 1337)
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Tampering Demonstration Lab Box */}
        <div className="tamper-demo-box">
          <h4>Tamper-Evidence Evaluation Lab</h4>
          <p>Subtly alter a single byte in the output media to test cryptographic tamper detection.</p>
          <div className="tamper-btn-row">
            <button className="danger-btn" onClick={() => handleTamperAction('tamper')}>
              ⚡ Modify Local Image Bytes (Tamper)
            </button>
            <button className="secondary-action-btn" onClick={() => handleTamperAction('restore')}>
              ↺ Restore Original Image Bytes
            </button>
          </div>
          {tamperStatus && (
            <div className="tamper-status-msg">
              {tamperStatus.is_tampered
                ? '⚠️ Local image bytes modified! Re-run verification to see tamper detection.'
                : '✓ Original image restored successfully.'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
