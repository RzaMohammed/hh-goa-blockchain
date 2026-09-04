import React, { useRef, useEffect } from 'react';
import { ASSETS } from '../../assets/datasets';

export default function BiometricViewport({
  currentKey,
  onCustomUpload,
  threshold,
  setThreshold,
  searchProvider,
  setSearchProvider,
  onRunPipeline,
  isRunning
}) {
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = 640;
    canvas.height = 360;

    const img = new Image();
    img.src = ASSETS[currentKey] || ASSETS.person;
    img.onload = () => {
      ctx.fillStyle = "#060c08";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 130, 20, 380, 320);

      if (currentKey === 'noface') {
        return;
      }

      // Restrained Bounding Box
      const x = 210, y = 70, w = 220, h = 220;

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
      ctx.fillRect(x, y - 20, 164, 18);
      ctx.fillStyle = "#facc15";
      ctx.font = "11px 'JetBrains Mono', monospace";
      ctx.fillText("YuNet DNN: 512-d Vector", x + 6, y - 6);
    };
  }, [currentKey]);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const buf = await file.arrayBuffer();
    const digest = await crypto.subtle.digest('SHA-256', buf);
    const hash = Array.from(new Uint8Array(digest))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    const reader = new FileReader();
    reader.onload = (evt) => {
      onCustomUpload(evt.target.result, hash, file.name);
    };
    reader.readAsDataURL(file);
  };

  const isNoFace = currentKey === 'noface';

  return (
    <div className="console-panel">
      <div className="panel-header-row">
        <span className="panel-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
          </svg>
          Stage 1: Biometric Face Analysis
        </span>
        <span className="nav-tag" id="activeModelTag">YuNet + SFace</span>
      </div>

      {/* Viewport Canvas */}
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
            {isNoFace ? '0 FACES DETECTED' : '5-PT ALIGNED'}
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className="form-group-row">
        <div className="form-control-block">
          <label className="control-title">
            <span>Similarity Threshold</span>
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

        <div className="form-control-block">
          <label className="control-title">Search Provider</label>
          <select
            className="ui-select"
            value={searchProvider}
            onChange={(e) => setSearchProvider(e.target.value)}
          >
            <option value="serpapi">SerpApi (Google Lens)</option>
            <option value="serper">Serper.dev Web Index</option>
            <option value="direct">Direct Local Corpus</option>
          </select>
        </div>
      </div>

      <button
        className="btn-action-primary"
        onClick={onRunPipeline}
        disabled={isRunning}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polygon points="5 3 19 12 5 21 5 3" />
        </svg>
        <span>{isRunning ? 'Processing Pipeline...' : 'Run Identification Pipeline'}</span>
      </button>

      {/* Upload Custom File Link */}
      <div style={{ marginTop: '12px', textAlign: 'center' }}>
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <button
          className="nav-tag"
          style={{ cursor: 'pointer', background: 'transparent' }}
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
        >
          + Upload custom local portrait
        </button>
      </div>
    </div>
  );
}
