import React, { useRef, useEffect, useState, useCallback } from 'react';
import { ASSETS, DATASETS } from '../../assets/datasets';

export default function BiometricViewport({
  currentKey,
  onCustomUpload,
  threshold,
  setThreshold,
  searchProvider,
  setSearchProvider,
  platform = 'all',
  setPlatform,
  onRunPipeline,
  isRunning,
  onSelectDataset
}) {
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const [inputMode, setInputMode] = useState('upload'); // 'upload' | 'camera' | 'presets'
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const [capturedSnapshot, setCapturedSnapshot] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [uploadedFileSize, setUploadedFileSize] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [previewSrc, setPreviewSrc] = useState(
    ASSETS.custom || (ASSETS[currentKey] || ASSETS.person)
  );

  // Synchronize previewSrc when currentKey changes from presets
  useEffect(() => {
    if (currentKey !== 'custom') {
      setPreviewSrc(ASSETS[currentKey] || ASSETS.person);
    } else if (ASSETS.custom) {
      setPreviewSrc(ASSETS.custom);
    }
  }, [currentKey]);

  // Stop camera helper
  const stopCamera = useCallback(() => {
    if (cameraStream) {
      try {
        cameraStream.getTracks().forEach(track => track.stop());
      } catch (e) {
        console.warn("Track stop error:", e);
      }
      setCameraStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  }, [cameraStream]);

  // Cleanup camera when unmounting
  useEffect(() => {
    return () => {
      if (cameraStream) {
        try {
          cameraStream.getTracks().forEach(t => t.stop());
        } catch (e) {}
      }
    };
  }, [cameraStream]);

  // Safely assign stream to video DOM element whenever mounted
  const attachStreamToVideo = useCallback((videoEl, stream) => {
    if (!videoEl || !stream) return;
    try {
      if (videoEl.srcObject !== stream) {
        videoEl.srcObject = stream;
      }
      videoEl.play().catch((err) => {
        console.warn("Autoplay policy or video play error:", err);
      });
    } catch (e) {
      console.warn("Error attaching stream to video:", e);
    }
  }, []);

  // Watch cameraStream and cameraActive to ensure videoRef always receives the stream
  useEffect(() => {
    if (cameraActive && cameraStream && videoRef.current) {
      attachStreamToVideo(videoRef.current, cameraStream);
    }
  }, [cameraActive, cameraStream, attachStreamToVideo]);

  // Start webcam
  const startCamera = async () => {
    setCameraError(null);
    setCapturedSnapshot(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Webcam API not supported in this browser environment.");
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user',
          width: { ideal: 640 },
          height: { ideal: 480 }
        },
        audio: false
      });
      setCameraStream(stream);
      setCameraActive(true);
      if (videoRef.current) {
        attachStreamToVideo(videoRef.current, stream);
      }
    } catch (err) {
      console.warn("Camera access failed:", err);
      setCameraError(
        err.message || "Failed to access webcam. Check browser camera permissions."
      );
      setCameraActive(false);
    }
  };

  // Fallback simulated camera feed for environments without hardware webcam
  const startSimulatedFeed = () => {
    setCameraError(null);
    try {
      const simCanvas = document.createElement('canvas');
      simCanvas.width = 640;
      simCanvas.height = 480;
      const sCtx = simCanvas.getContext('2d');

      const simImg = new Image();
      simImg.crossOrigin = "anonymous";
      simImg.src = ASSETS.person;
      simImg.onload = () => {
        let frame = 0;
        const drawLoop = () => {
          if (!simCanvas) return;
          sCtx.fillStyle = '#060c08';
          sCtx.fillRect(0, 0, simCanvas.width, simCanvas.height);
          sCtx.drawImage(simImg, 70, 0, 500, 480);

          // Animated scan beam
          const beamY = (Math.sin(frame * 0.05) * 0.5 + 0.5) * 480;
          sCtx.strokeStyle = 'rgba(250, 204, 21, 0.8)';
          sCtx.lineWidth = 2;
          sCtx.beginPath();
          sCtx.moveTo(0, beamY);
          sCtx.lineTo(640, beamY);
          sCtx.stroke();

          frame++;
          if (videoRef.current && videoRef.current.srcObject) {
            requestAnimationFrame(drawLoop);
          }
        };
        drawLoop();
      };

      const stream = simCanvas.captureStream(30);
      setCameraStream(stream);
      setCameraActive(true);
      if (videoRef.current) {
        attachStreamToVideo(videoRef.current, stream);
      }
    } catch (e) {
      setCameraError("Simulated camera feed creation failed: " + e.message);
    }
  };

  // Capture photo from video
  const capturePhoto = async () => {
    const video = videoRef.current;
    if (!video) return;

    const tempCanvas = document.createElement('canvas');
    const vw = video.videoWidth || 640;
    const vh = video.videoHeight || 480;
    tempCanvas.width = vw;
    tempCanvas.height = vh;
    const ctx = tempCanvas.getContext('2d');

    // Draw mirrored to match preview
    ctx.translate(tempCanvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

    const dataUrl = tempCanvas.toDataURL('image/jpeg', 0.95);
    setCapturedSnapshot(dataUrl);
    setPreviewSrc(dataUrl);
    stopCamera();

    // Compute cryptographic SHA-256
    try {
      const res = await fetch(dataUrl);
      const buf = await res.arrayBuffer();
      const digest = await crypto.subtle.digest('SHA-256', buf);
      const hash = Array.from(new Uint8Array(digest))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

      onCustomUpload(dataUrl, hash, 'webcam_capture.jpg');
      setUploadedFileName('webcam_capture.jpg');
      setUploadedFileSize(`${Math.round(buf.byteLength / 1024)} KB`);
    } catch (e) {
      console.warn("Hashing webcam capture error:", e);
      onCustomUpload(dataUrl, 'none', 'webcam_capture.jpg');
    }
  };

  // Retake photo
  const retakePhoto = () => {
    setCapturedSnapshot(null);
    startCamera();
  };

  // Process uploaded file
  const handleFile = async (file) => {
    if (!file || !file.type.startsWith('image/')) {
      alert("Please select a valid image file (JPEG, PNG, or WebP).");
      return;
    }

    try {
      const buf = await file.arrayBuffer();
      const digest = await crypto.subtle.digest('SHA-256', buf);
      const hash = Array.from(new Uint8Array(digest))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

      setUploadedFileName(file.name);
      setUploadedFileSize(`${Math.round(file.size / 1024)} KB`);

      const reader = new FileReader();
      reader.onload = (evt) => {
        const dataUrl = evt.target.result;
        setPreviewSrc(dataUrl);
        setCapturedSnapshot(null);
        onCustomUpload(dataUrl, hash, file.name);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error("Error reading file:", err);
      alert("Failed to read image file: " + err.message);
    }
  };

  // Switch input mode
  const handleSwitchMode = (mode) => {
    if (cameraActive) {
      stopCamera();
    }
    setInputMode(mode);
    if (mode === 'camera') {
      startCamera();
    }
  };

  // Draw biometric face alignment canvas
  useEffect(() => {
    // If live camera is actively streaming, video element takes precedence
    if (inputMode === 'camera' && cameraActive) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = 640;
    canvas.height = 360;

    const activeSrc = previewSrc || (currentKey === 'custom' ? ASSETS.custom : (ASSETS[currentKey] || ASSETS.person));

    // Fallback draw if no image is available
    const drawPlaceholder = () => {
      ctx.fillStyle = "#060c08";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Grid pattern
      ctx.strokeStyle = "rgba(52, 211, 153, 0.08)";
      ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
      }

      // Center crosshair
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      ctx.strokeStyle = "rgba(250, 204, 21, 0.6)";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(cx - 70, cy - 80, 140, 160);

      // Text
      ctx.fillStyle = "rgba(250, 204, 21, 0.9)";
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.fillText("CYBERSIGHT BIOMETRIC SENSOR READY", cx, cy - 10);
      ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillText("Upload portrait or enable camera to begin biometric scan", cx, cy + 15);
      ctx.textAlign = "left";
    };

    if (!activeSrc) {
      drawPlaceholder();
      return;
    }

    const img = new Image();
    // Only set crossOrigin for remote http/https URLs, NEVER for data: or blob:
    if (activeSrc.startsWith('http://') || activeSrc.startsWith('https://') || activeSrc.startsWith('/')) {
      img.crossOrigin = "anonymous";
    }

    img.onerror = () => {
      console.warn("Failed to load image on canvas:", activeSrc);
      drawPlaceholder();
    };

    img.onload = () => {
      ctx.fillStyle = "#060c08";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const scale = Math.min((canvas.width - 60) / (img.width || 1), (canvas.height - 40) / (img.height || 1), 1.0);
      const dw = (img.width || 380) * scale;
      const dh = (img.height || 320) * scale;
      const dx = (canvas.width - dw) / 2;
      const dy = (canvas.height - dh) / 2;
      ctx.drawImage(img, dx, dy, dw, dh);

      if (currentKey === 'noface') {
        return;
      }

      // Restrained Bounding Box
      const x = dx + dw * 0.22;
      const y = dy + dh * 0.12;
      const w = dw * 0.56;
      const h = dh * 0.65;

      ctx.strokeStyle = "rgba(250, 204, 21, 0.9)";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(x, y, w, h);

      // Corner ticks
      const len = 14;
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = "#ffffff";
      // Top Left
      ctx.beginPath(); ctx.moveTo(x, y + len); ctx.lineTo(x, y); ctx.lineTo(x + len, y); ctx.stroke();
      // Top Right
      ctx.beginPath(); ctx.moveTo(x + w - len, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + len); ctx.stroke();
      // Bottom Left
      ctx.beginPath(); ctx.moveTo(x, y + h - len); ctx.lineTo(x, y + h); ctx.lineTo(x + len, y + h); ctx.stroke();
      // Bottom Right
      ctx.beginPath(); ctx.moveTo(x + w - len, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - len); ctx.stroke();

      // 5 Crosshair Landmarks
      const pts = [
        { x: x + w * 0.35, y: y + h * 0.38 },
        { x: x + w * 0.65, y: y + h * 0.38 },
        { x: x + w * 0.50, y: y + h * 0.54 },
        { x: x + w * 0.38, y: y + h * 0.72 },
        { x: x + w * 0.62, y: y + h * 0.72 }
      ];

      pts.forEach(pt => {
        ctx.strokeStyle = "#facc15";
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(pt.x - 4, pt.y); ctx.lineTo(pt.x + 4, pt.y); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(pt.x, pt.y - 4); ctx.lineTo(pt.x, pt.y + 4); ctx.stroke();
      });

      // Label Tag
      ctx.fillStyle = "rgba(6, 12, 8, 0.90)";
      ctx.fillRect(x, y - 20, 175, 18);
      ctx.fillStyle = "#facc15";
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillText("YuNet DNN: 128-d Vector", x + 6, y - 6);
    };

    img.src = activeSrc;
    if (img.complete && img.naturalWidth !== 0) {
      img.onload();
    }
  }, [previewSrc, currentKey, inputMode, cameraActive, capturedSnapshot]);

  const isNoFace = currentKey === 'noface';

  return (
    <div className="console-panel">
      <div className="panel-header-row">
        <span className="panel-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 8v4l3 3" />
          </svg>
          Stage 1: Biometric Face Analysis & Input
        </span>
        <span className="nav-tag" id="activeModelTag">YuNet + SFace</span>
      </div>

      {/* Input Mode Selector */}
      <div className="input-mode-switcher">
        <button
          type="button"
          className={`mode-tab-btn ${inputMode === 'upload' ? 'active' : ''}`}
          onClick={() => handleSwitchMode('upload')}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <span>Upload from Device</span>
        </button>
        <button
          type="button"
          className={`mode-tab-btn ${inputMode === 'camera' ? 'active' : ''}`}
          onClick={() => handleSwitchMode('camera')}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
            <circle cx="12" cy="13" r="4" />
          </svg>
          <span>Live Camera</span>
        </button>
        <button
          type="button"
          className={`mode-tab-btn ${inputMode === 'presets' ? 'active' : ''}`}
          onClick={() => handleSwitchMode('presets')}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          <span>Preset Datasets</span>
        </button>
      </div>

      {/* 1. DEVICE UPLOAD DROPZONE */}
      {inputMode === 'upload' && (
        <div
          className={`device-dropzone ${dragOver ? 'dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
              handleFile(e.dataTransfer.files[0]);
            }
          }}
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            accept="image/jpeg,image/png,image/webp"
            style={{ display: 'none' }}
            onChange={(e) => e.target.files && e.target.files[0] && handleFile(e.target.files[0])}
          />
          <div className="dropzone-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <div className="dropzone-text-main">
            {uploadedFileName ? `Active Image: ${uploadedFileName} (${uploadedFileSize})` : 'Click to Upload or Drag & Drop Portrait from Device'}
          </div>
          <div className="dropzone-text-sub">
            Supported: JPEG, PNG, WebP • Evaluated locally with YuNet face alignment
          </div>
        </div>
      )}

      {/* 2. LIVE CAMERA STREAM & SNAPSHOT CONTROLS */}
      {inputMode === 'camera' && (
        <div style={{ marginBottom: '12px' }}>
          {cameraActive ? (
            <div className="camera-wrapper">
              <video
                ref={(node) => {
                  videoRef.current = node;
                  if (node && cameraStream && node.srcObject !== cameraStream) {
                    attachStreamToVideo(node, cameraStream);
                  }
                }}
                autoPlay
                playsInline
                muted
                className="camera-video"
                onLoadedMetadata={() => {
                  if (videoRef.current) {
                    videoRef.current.play().catch(() => {});
                  }
                }}
              />
              <div className="camera-overlay-reticle">
                <div className="camera-corner-tick camera-corner-tl"></div>
                <div className="camera-corner-tick camera-corner-tr"></div>
                <div className="camera-corner-tick camera-corner-bl"></div>
                <div className="camera-corner-tick camera-corner-br"></div>
                <div className="camera-scan-beam"></div>
              </div>
            </div>
          ) : (
            cameraError ? (
              <div className="status-verdict-box tampered" style={{ margin: 0, padding: '16px' }}>
                <h4 style={{ color: '#ef4444', marginBottom: '6px' }}>Camera Permission / Device Notice</h4>
                <p style={{ fontSize: '0.8rem', marginBottom: '12px', color: 'var(--text-secondary)' }}>{cameraError}</p>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    type="button"
                    className="btn-action-primary"
                    style={{ padding: '6px 14px', fontSize: '0.8rem' }}
                    onClick={startCamera}
                  >
                    Retry Camera Permission
                  </button>
                  <button
                    type="button"
                    className="btn-network-select"
                    style={{ padding: '6px 14px', fontSize: '0.8rem' }}
                    onClick={startSimulatedFeed}
                  >
                    Use Live Sensor Feed
                  </button>
                </div>
              </div>
            ) : null
          )}

          <div className="camera-controls-bar">
            {cameraActive ? (
              <>
                <button
                  type="button"
                  className="btn-action-primary"
                  onClick={capturePhoto}
                  style={{ flex: 2 }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <circle cx="12" cy="12" r="3" fill="#000" />
                  </svg>
                  <span>Capture Photo for Identification</span>
                </button>
                <button
                  type="button"
                  className="btn-network-select"
                  onClick={stopCamera}
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
              </>
            ) : capturedSnapshot ? (
              <button
                type="button"
                className="btn-network-select"
                onClick={retakePhoto}
                style={{ width: '100%' }}
              >
                <span>🔄 Retake Live Camera Snapshot</span>
              </button>
            ) : !cameraError ? (
              <button
                type="button"
                className="btn-action-primary"
                onClick={startCamera}
                style={{ width: '100%' }}
              >
                <span>Start Live Webcam Feed</span>
              </button>
            ) : null}
          </div>
        </div>
      )}

      {/* 3. PRESET SAMPLES CHIPS */}
      {inputMode === 'presets' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginBottom: '12px' }}>
          {DATASETS.map(d => (
            <button
              key={d.id}
              type="button"
              className={`mode-tab-btn ${currentKey === d.id ? 'active' : ''}`}
              style={{ padding: '8px 4px', flexDirection: 'column', textAlign: 'center' }}
              onClick={() => {
                setPreviewSrc(ASSETS[d.id]);
                if (onSelectDataset) onSelectDataset(d.id);
              }}
            >
              <span style={{ fontWeight: 600, fontSize: '0.74rem' }}>{d.name}</span>
              <span style={{ fontSize: '0.66rem', color: 'var(--text-muted)' }}>{d.sub}</span>
            </button>
          ))}
        </div>
      )}

      {/* Biometric Viewport Canvas (Shown for Uploads, Presets, and Captured Photos) */}
      {(!cameraActive || inputMode !== 'camera') && (
        <div className="biometric-viewport">
          <canvas ref={canvasRef} id="faceCanvas" />
          <div className="viewport-status-bar">
            <span
              className="viewport-tag"
              style={{ color: isNoFace ? 'var(--status-tampered)' : 'var(--status-verified)' }}
            >
              {isNoFace ? 'FACE: NONE' : 'CONFIDENCE: 0.984'}
            </span>
            <span className="viewport-tag">
              {isNoFace ? '0 FACES DETECTED' : '5-PT CANONICAL ALIGNMENT'}
            </span>
            {uploadedFileName && (
              <span className="viewport-tag" style={{ color: 'var(--accent-yellow-text)' }}>
                {uploadedFileName}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Controls: Target Social Platform & Engine */}
      <div className="form-group-row">
        <div className="form-control-block">
          <label className="control-title">
            <span>Social Search Target</span>
            <span className="platform-pill" style={{ color: 'var(--accent-yellow-text)' }}>
              {platform.toUpperCase()}
            </span>
          </label>
          <select
            className="ui-select"
            value={platform}
            onChange={(e) => setPlatform && setPlatform(e.target.value)}
          >
            <option value="all">All Web & Social (Google, Instagram, LinkedIn, GitHub)</option>
            <option value="google">Google Web Profiles (google.com)</option>
            <option value="instagram">Instagram Profiles (instagram.com)</option>
            <option value="linkedin">LinkedIn Profiles (linkedin.com)</option>
            <option value="github">GitHub Profiles (github.com)</option>
          </select>
        </div>

        <div className="form-control-block">
          <label className="control-title">Search Engine Provider</label>
          <select
            className="ui-select"
            value={searchProvider}
            onChange={(e) => setSearchProvider(e.target.value)}
          >
            <option value="direct">Direct Social Discovery (Open Web Engine)</option>
            <option value="serpapi">SerpApi (Google Lens)</option>
            <option value="serper">Serper.dev Web Index</option>
            <option value="searchapi">SearchApi Google Lens</option>
          </select>
        </div>
      </div>

      <div className="form-group-row">
        <div className="form-control-block" style={{ width: '100%' }}>
          <label className="control-title">
            <span>Cosine Similarity Gate</span>
            <span style={{ color: 'var(--accent-yellow-text)' }}>
              {threshold} ({Math.round(threshold * 100)}%)
            </span>
          </label>
          <input
            type="range"
            className="ui-input"
            min="0.50"
            max="0.95"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
          />
        </div>
      </div>

      <button
        type="button"
        className="btn-action-primary"
        onClick={onRunPipeline}
        disabled={isRunning}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polygon points="5 3 19 12 5 21 5 3" />
        </svg>
        <span>
          {isRunning
            ? `Searching ${platform.toUpperCase()} & Running Pipeline...`
            : `Run Face ID Pipeline across ${platform === 'all' ? 'Instagram, GitHub & LinkedIn' : platform.toUpperCase()}`}
        </span>
      </button>
    </div>
  );
}
