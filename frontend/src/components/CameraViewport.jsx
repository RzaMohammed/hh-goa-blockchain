import React, { useRef, useEffect, useState, useCallback } from 'react';

export default function CameraViewport({
  mode,
  setMode,
  customImage,
  setCustomImage,
  onCapture,
  pipelineState,
  onResetState
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [faceDetected, setFaceDetected] = useState(false);
  const [faceStatusText, setFaceStatusText] = useState('INITIALIZING CAMERA...');
  const [shutterFlash, setShutterFlash] = useState(false);
  const [capturedPreview, setCapturedPreview] = useState(null);

  // Target Social & Identity Discovery State
  const [targetName, setTargetName] = useState('');
  const [targetPlatform, setTargetPlatform] = useState('all');
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [enrollName, setEnrollName] = useState('');
  const [enrollHandle, setEnrollHandle] = useState('');
  const [enrollStatus, setEnrollStatus] = useState(null);
  const [enrolling, setEnrolling] = useState(false);

  // Smooth bounding box tracking target
  const targetBoxRef = useRef(null);
  const currentBoxRef = useRef(null);
  const animFrameIdRef = useRef(null);

  // Initialize Webcam Stream
  const startCamera = async () => {
    setCameraError(null);
    setFaceStatusText('STARTING CAMERA...');
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Webcam API is not supported in this browser environment.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.muted = true;
        videoRef.current.setAttribute('playsinline', '');
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play().then(() => {
            setCameraActive(true);
            setFaceStatusText('CAMERA ACTIVE - READY');
          }).catch(e => {
            console.log('Autoplay handled:', e);
            setCameraActive(true);
          });
        };
      }
    } catch (err) {
      console.warn('Webcam access error:', err);
      setCameraError(err.message || 'Webcam access failed. You can switch to Upload File mode.');
      setCameraActive(false);
      setFaceStatusText('CAMERA UNAVAILABLE');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  };

  useEffect(() => {
    if (mode === 'webcam') {
      startCamera();
    } else {
      stopCamera();
      setFaceDetected(true);
      setFaceStatusText(customImage ? 'IMAGE LOADED' : 'SELECT IMAGE');
    }
    return () => {
      stopCamera();
      if (animFrameIdRef.current) cancelAnimationFrame(animFrameIdRef.current);
    };
  }, [mode]);

  // Real-time Face Detection Loop (window.FaceDetector + Canvas Feature Centroid Fallback)
  const runFaceDetectorLoop = useCallback(() => {
    if (mode !== 'webcam' || !videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (video.readyState < 2) {
      animFrameIdRef.current = requestAnimationFrame(runFaceDetectorLoop);
      return;
    }

    const vw = video.videoWidth || 640;
    const vh = video.videoHeight || 480;
    canvas.width = vw;
    canvas.height = vh;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, vw, vh);

    const detectNative = async () => {
      if ('FaceDetector' in window) {
        try {
          const detector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 1 });
          const faces = await detector.detect(video);
          if (faces && faces.length > 0) {
            const b = faces[0].boundingBox;
            return { x: b.x, y: b.y, width: b.width, height: b.height };
          }
        } catch (e) {
          // Native detector error fallback
        }
      }
      return null;
    };

    const detectFallback = () => {
      try {
        const offscreen = document.createElement('canvas');
        offscreen.width = 160;
        offscreen.height = 120;
        const octx = offscreen.getContext('2d');
        octx.drawImage(video, 0, 0, 160, 120);
        const imgData = octx.getImageData(0, 0, 160, 120);
        const data = imgData.data;

        let sumX = 0, sumY = 0, count = 0;
        let minX = 160, maxX = 0, minY = 120, maxY = 0;

        for (let y = 0; y < 120; y += 2) {
          for (let x = 0; x < 160; x += 2) {
            const idx = (y * 160 + x) * 4;
            const r = data[idx];
            const g = data[idx + 1];
            const b = data[idx + 2];
            if (r > 60 && g > 40 && b > 20 && r > g && r > b && Math.abs(r - g) > 15) {
              sumX += x;
              sumY += y;
              count++;
              if (x < minX) minX = x;
              if (x > maxX) maxX = x;
              if (y < minY) minY = y;
              if (y > maxY) maxY = y;
            }
          }
        }

        if (count > 250) {
          const scaleX = vw / 160;
          const scaleY = vh / 120;
          const width = Math.max(120, (maxX - minX) * scaleX * 1.1);
          const height = Math.max(140, (maxY - minY) * scaleY * 1.2);
          const cx = (sumX / count) * scaleX;
          const cy = (sumY / count) * scaleY;
          const x = Math.max(10, Math.min(vw - width - 10, cx - width / 2));
          const y = Math.max(10, Math.min(vh - height - 10, cy - height * 0.45));
          return { x, y, width, height };
        }
      } catch (e) {
        // Ignore fallback error
      }
      return null;
    };

    detectNative().then(nativeBox => {
      const box = nativeBox || detectFallback();

      if (box) {
        targetBoxRef.current = box;
        setFaceDetected(true);
        if (pipelineState === 'idle') {
          setFaceStatusText('FACE DETECTED - READY');
        }
      } else {
        targetBoxRef.current = null;
        setFaceDetected(false);
        if (pipelineState === 'idle') {
          setFaceStatusText('CAMERA ACTIVE - POSITION FACE');
        }
      }

      // Smooth LERP interpolation for current box
      if (targetBoxRef.current) {
        if (!currentBoxRef.current) {
          currentBoxRef.current = { ...targetBoxRef.current };
        } else {
          const lerp = (a, b) => a + (b - a) * 0.35;
          currentBoxRef.current = {
            x: lerp(currentBoxRef.current.x, targetBoxRef.current.x),
            y: lerp(currentBoxRef.current.y, targetBoxRef.current.y),
            width: lerp(currentBoxRef.current.width, targetBoxRef.current.width),
            height: lerp(currentBoxRef.current.height, targetBoxRef.current.height),
          };
        }

        // Draw Futuristic Target Bounding Box Brackets
        const { x, y, width: w, height: h } = currentBoxRef.current;
        const cornerLen = Math.min(28, w * 0.25);
        ctx.strokeStyle = '#00f2fe';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = '#00f2fe';
        ctx.shadowBlur = 12;

        // Corners
        ctx.beginPath(); ctx.moveTo(x, y + cornerLen); ctx.lineTo(x, y); ctx.lineTo(x + cornerLen, y); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + w - cornerLen, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + cornerLen); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + w, y + h - cornerLen); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - cornerLen, y + h); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + cornerLen, y + h); ctx.lineTo(x, y + h); ctx.lineTo(x, y + h - cornerLen); ctx.stroke();

        ctx.fillStyle = '#00f2fe';
        ctx.beginPath();
        ctx.arc(x + w / 2, y + h / 2, 3, 0, Math.PI * 2);
        ctx.fill();
      } else {
        currentBoxRef.current = null;
      }

      animFrameIdRef.current = requestAnimationFrame(runFaceDetectorLoop);
    });
  }, [mode, pipelineState]);

  useEffect(() => {
    if (mode === 'webcam' && cameraActive) {
      animFrameIdRef.current = requestAnimationFrame(runFaceDetectorLoop);
    }
  }, [mode, cameraActive, runFaceDetectorLoop]);

  // Handle File Upload
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        const b64 = evt.target?.result;
        setCustomImage(b64);
        setCapturedPreview(b64);
        setFaceDetected(true);
        setFaceStatusText('IMAGE READY - VERIFYING');
        if (onResetState) onResetState();
        onCapture(b64);
      };
      reader.readAsDataURL(file);
    }
  };

  // Capture Photo Trigger from Live Webcam Video Frame
  const handleTriggerCapture = () => {
    // If in upload mode and no image uploaded yet, trigger file picker
    if (mode === 'upload' && !customImage) {
      fileInputRef.current?.click();
      return;
    }

    let capturedB64 = null;

    if (mode === 'webcam') {
      // Trigger shutter flash visual feedback
      setShutterFlash(true);
      setTimeout(() => setShutterFlash(false), 250);

      const v = videoRef.current;
      if (v && (v.readyState >= 1 || v.videoWidth > 0)) {
        try {
          const c = document.createElement('canvas');
          c.width = v.videoWidth || 1280;
          c.height = v.videoHeight || 720;
          const ctx = c.getContext('2d');
          ctx.drawImage(v, 0, 0, c.width, c.height);
          capturedB64 = c.toDataURL('image/jpeg', 0.95);
          setCapturedPreview(capturedB64);
        } catch (e) {
          console.warn('Canvas capture error:', e);
        }
      }

      // If video stream is not active or available, smoothly open device camera/file picker
      if (!capturedB64) {
        setFaceStatusText('SELECT PHOTO TO VERIFY');
        fileInputRef.current?.click();
        return;
      }
    } else if (mode === 'upload' && customImage) {
      capturedB64 = customImage;
    }

    if (capturedB64) {
      onCapture(capturedB64, {
        target_name: targetName.trim(),
        platform: targetPlatform
      });
    }
  };

  const handleEnrollFace = async () => {
    let photoB64 = capturedPreview || customImage;
    if (!photoB64 && mode === 'webcam') {
      const v = videoRef.current;
      if (v && (v.readyState >= 1 || v.videoWidth > 0)) {
        try {
          const c = document.createElement('canvas');
          c.width = v.videoWidth || 1280;
          c.height = v.videoHeight || 720;
          const ctx = c.getContext('2d');
          ctx.drawImage(v, 0, 0, c.width, c.height);
          photoB64 = c.toDataURL('image/jpeg', 0.95);
        } catch (e) {
          console.warn('Canvas capture error:', e);
        }
      }
    }
    if (!photoB64) {
      setEnrollStatus({ error: 'Please click photo or select image first to enroll.' });
      return;
    }
    setEnrolling(true);
    setEnrollStatus(null);
    try {
      const res = await fetch('/api/enroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: photoB64,
          name: enrollName.trim() || 'Verified Identity',
          handle: enrollHandle.trim() || undefined,
          source_url: enrollHandle ? `https://github.com/${enrollHandle.replace('@', '')}` : undefined
        })
      });
      const data = await res.json();
      if (data.success) {
        setEnrollStatus({ success: true, message: `Face enrolled on Blockchain! Record #${data.record?.record_id || 1}` });
        setTimeout(() => setShowEnrollModal(false), 2200);
      } else {
        setEnrollStatus({ error: data.error || 'Failed to enroll identity.' });
      }
    } catch (e) {
      setEnrollStatus({ error: `Connection error: ${e.message}` });
    } finally {
      setEnrolling(false);
    }
  };

  const getBadgeStyle = () => {
    if (pipelineState === 'searching') return { bg: 'rgba(234, 179, 8, 0.15)', text: '#eab308', border: '#eab308' };
    if (pipelineState === 'verified') return { bg: 'rgba(16, 185, 129, 0.15)', text: '#10b981', border: '#10b981' };
    if (pipelineState === 'failed') return { bg: 'rgba(239, 68, 68, 0.15)', text: '#ef4444', border: '#ef4444' };
    if (cameraActive || customImage) return { bg: 'rgba(0, 242, 254, 0.12)', text: '#00f2fe', border: '#00f2fe' };
    return { bg: 'rgba(255, 255, 255, 0.05)', text: '#94a3b8', border: '#334155' };
  };

  const badgeStyle = getBadgeStyle();

  return (
    <div className="camera-workstation-panel">
      {/* Hidden file & device camera input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="user"
        onChange={handleFileUpload}
        style={{ display: 'none' }}
      />

      {/* Top Controls Bar */}
      <div className="viewport-top-bar">
        <div className="mode-toggle-group">
          <button
            className={`mode-btn ${mode === 'webcam' ? 'active' : ''}`}
            onClick={() => { setMode('webcam'); setCapturedPreview(null); if (onResetState) onResetState(); }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
            Live Camera
          </button>
          <button
            className={`mode-btn ${mode === 'upload' ? 'active' : ''}`}
            onClick={() => { setMode('upload'); if (onResetState) onResetState(); }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload File
          </button>
        </div>

        {/* Dynamic Status Pill */}
        <div
          className="live-status-pill"
          style={{
            background: badgeStyle.bg,
            color: badgeStyle.text,
            borderColor: badgeStyle.border
          }}
        >
          <span className="pulse-dot" style={{ background: badgeStyle.text }} />
          {pipelineState !== 'idle'
            ? pipelineState.toUpperCase()
            : faceStatusText}
        </div>
      </div>

      {/* Main Viewport Container */}
      <div className="viewport-stage">
        {shutterFlash && <div className="camera-shutter-flash" />}

        {mode === 'webcam' ? (
          <div className="webcam-wrapper">
            <video ref={videoRef} playsInline autoPlay muted className="webcam-video" />
            <canvas ref={canvasRef} className="webcam-overlay-canvas" />

            {cameraError && (
              <div className="viewport-fallback-notice">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <p style={{ color: '#ef4444', fontWeight: 600 }}>{cameraError}</p>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="secondary-action-btn" onClick={startCamera}>
                    ↻ Retry Camera
                  </button>
                  <button className="secondary-action-btn" onClick={() => setMode('upload')}>
                    Switch to Upload Mode
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="upload-preview-wrapper" onClick={() => fileInputRef.current?.click()} style={{ cursor: 'pointer' }}>
            {customImage ? (
              <img src={customImage} alt="Uploaded Face" className="stage-image-preview" />
            ) : (
              <div className="upload-placeholder-box">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="1.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <p>Click or drag photo here to upload</p>
                <span className="sub-text">Supports JPG, PNG, WebP</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Captured Snapshot Thumbnail Indicator */}
      {capturedPreview && (
        <div className="captured-snapshot-bar">
          <img src={capturedPreview} alt="Captured Snapshot" className="snapshot-thumb" />
          <div className="snapshot-info">
            <span className="snapshot-tag">✓ SNAPSHOT READY</span>
            <span className="snapshot-sub">Photo captured from live camera feed</span>
          </div>
        </div>
      )}

      {/* Target Discovery & Social Platform Bar */}
      <div className="discovery-control-card">
        <div className="discovery-card-header">
          <div className="discovery-card-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#00f2fe" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <span>Target Identity / Social Handle</span>
          </div>
          <span className="ai-constraint-badge">🛡️ Strict Human Face Constraint</span>
        </div>

        <div className="discovery-input-row">
          <div className="discovery-input-wrapper">
            <input
              type="text"
              className="discovery-text-input"
              placeholder="Search name or handle (e.g. Aditya Tomar, @username)..."
              value={targetName}
              onChange={(e) => setTargetName(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleTriggerCapture(); }}
            />
            {targetName && (
              <button
                type="button"
                className="clear-input-btn"
                onClick={() => setTargetName('')}
              >
                ✕
              </button>
            )}
          </div>

          <div className="platform-filter-pills">
            {[
              { id: 'all', label: '🌐 All Social' },
              { id: 'instagram', label: '📷 Instagram' },
              { id: 'linkedin', label: '💼 LinkedIn' },
              { id: 'github', label: '🐙 GitHub' }
            ].map(p => (
              <button
                key={p.id}
                type="button"
                className={`platform-btn-pill ${targetPlatform === p.id ? 'active' : ''}`}
                onClick={() => setTargetPlatform(p.id)}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Primary Action Button Bar */}
      <div className="viewport-action-bar">
        <button
          className={`primary-capture-btn ${pipelineState === 'searching' ? 'searching' : ''}`}
          disabled={pipelineState === 'searching'}
          onClick={handleTriggerCapture}
        >
          {pipelineState === 'searching' ? (
            <>
              <span className="btn-spinner" />
              SEARCHING & VERIFYING ON-CHAIN...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <circle cx="12" cy="12" r="10" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              {mode === 'webcam' ? '📸 CLICK PHOTO & VERIFY' : (customImage ? '⚡ START VERIFICATION' : '📂 SELECT IMAGE FILE')}
            </>
          )}
        </button>

        <button
          className="secondary-enroll-btn"
          type="button"
          disabled={pipelineState === 'searching'}
          onClick={() => {
            setEnrollName(targetName || '');
            setShowEnrollModal(true);
            setEnrollStatus(null);
          }}
          title="Enroll your face to the Blockchain Ledger so future scans match your registered identity"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00f2fe" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="M12 8v8" />
            <path d="M8 12h8" />
          </svg>
          Enroll on Blockchain
        </button>
      </div>

      {/* Enroll Identity Modal */}
      {showEnrollModal && (
        <div className="modal-overlay" onClick={() => setShowEnrollModal(false)}>
          <div className="enroll-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-row">
                <span className="modal-icon">🛡️</span>
                <h3>Enroll Face to Blockchain</h3>
              </div>
              <button className="modal-close-btn" onClick={() => setShowEnrollModal(false)}>✕</button>
            </div>

            <p className="modal-desc">
              Register your facial biometric template and SHA-256 fingerprint on the local Ganache EVM smart contract. Future scans will immediately recognize you with 99%+ biometric confidence.
            </p>

            <div className="modal-form-group">
              <label>Full Name / Identity Title</label>
              <input
                type="text"
                placeholder="e.g. Aditya Pratap Singh Tomar"
                value={enrollName}
                onChange={(e) => setEnrollName(e.target.value)}
              />
            </div>

            <div className="modal-form-group">
              <label>Social Handle / Profile URL (Optional)</label>
              <input
                type="text"
                placeholder="e.g. @adityatomar or https://github.com/vvgaditya-8123"
                value={enrollHandle}
                onChange={(e) => setEnrollHandle(e.target.value)}
              />
            </div>

            {enrollStatus && (
              <div className={`enroll-status-msg ${enrollStatus.success ? 'success' : 'error'}`}>
                {enrollStatus.success ? `✓ ${enrollStatus.message}` : `⚠️ ${enrollStatus.error}`}
              </div>
            )}

            <div className="modal-action-row">
              <button
                type="button"
                className="cancel-modal-btn"
                onClick={() => setShowEnrollModal(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="confirm-enroll-btn"
                disabled={enrolling}
                onClick={handleEnrollFace}
              >
                {enrolling ? 'NOTARIZING ON EVM...' : '⚡ CONFIRM & NOTARIZE ON-CHAIN'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
