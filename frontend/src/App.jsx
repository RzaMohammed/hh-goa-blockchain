import React, { useState, useEffect } from 'react';
import CameraViewport from './components/CameraViewport';
import ProcessStageStepper from './components/ProcessStageStepper';
import MatchResultsCard from './components/MatchResultsCard';
import VerificationView from './components/VerificationView';
import HistoryView from './components/HistoryView';

export default function App() {
  // Navigation & View State
  const [activeTab, setActiveTab] = useState('workstation'); // 'workstation', 'verification', 'history'
  const [mode, setMode] = useState('webcam'); // 'webcam', 'upload'
  const [customImage, setCustomImage] = useState(null);

  // Pipeline Execution State
  const [pipelineState, setPipelineState] = useState('idle'); // 'idle', 'searching', 'verified', 'failed'
  const [currentStage, setCurrentStage] = useState(1);
  const [pipelineResults, setPipelineResults] = useState(null);
  const [statusInfo, setStatusInfo] = useState(null);

  // Fetch status on mount & polling
  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      setStatusInfo(data);
    } catch (e) {
      console.warn('Status fetch error:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleResetState = () => {
    setPipelineState('idle');
    setCurrentStage(1);
    setPipelineResults(null);
  };

  // Run Pipeline Execution for Captured Webcam Snapshot or File Upload
  const handleCaptureAndRun = async (capturedB64Image, options = {}) => {
    setPipelineState('searching');
    setCurrentStage(1);
    setPipelineResults(null);

    const imagePayload = capturedB64Image || customImage;
    const targetName = options.target_name || '';
    const platform = options.platform || 'all';

    try {
      // Stage 1: Face Detection
      setCurrentStage(1);
      await new Promise(r => setTimeout(r, 150));

      // Stage 2: Web Search
      setCurrentStage(2);
      const res = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_id: 'custom',
          threshold: 0.55,
          provider: 'serpapi',
          platform: platform,
          target_name: targetName,
          custom_image: imagePayload
        })
      });

      const data = await res.json();

      if (!data.success) {
        setPipelineState('failed');
        setPipelineResults({
          verdict: data.verdict || {
            type: 'noface',
            title: 'No Face Detected',
            message: data.error || 'YuNet detector found zero human faces in the provided frame. Please ensure your face is clearly visible.'
          }
        });
        return;
      }

      // Stage 3: Match Evaluation
      setCurrentStage(3);
      await new Promise(r => setTimeout(r, 200));

      // Stage 4: SHA-256 Fingerprint
      setCurrentStage(4);
      await new Promise(r => setTimeout(r, 150));

      // Stage 5: Blockchain Notarization
      setCurrentStage(5);
      await new Promise(r => setTimeout(r, 250));

      // Pipeline Complete
      setCurrentStage(6);
      setPipelineState('verified');
      setPipelineResults(data);
      fetchStatus();

    } catch (err) {
      setPipelineState('failed');
      setPipelineResults({
        verdict: {
          type: 'failed',
          title: 'Pipeline Connection Error',
          message: `Could not connect to backend server: ${err.message}`
        }
      });
    }
  };

  return (
    <div className="workstation-app-container">
      {/* 1. TOP FUTURISTIC HEADER */}
      <header className="workstation-navbar">
        <div className="nav-brand">
          <div className="brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00f2fe" strokeWidth="2.2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <div className="brand-text">
            <span className="brand-name">CYBERSIGHT</span>
            <span className="brand-tag">FACE WORKSTATION</span>
          </div>
        </div>

        {/* Minimal Navigation View Switcher */}
        <nav className="nav-view-switcher">
          <button
            className={`nav-tab-btn ${activeTab === 'workstation' ? 'active' : ''}`}
            onClick={() => setActiveTab('workstation')}
          >
            FACE VERIFY
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'verification' ? 'active' : ''}`}
            onClick={() => setActiveTab('verification')}
          >
            INTEGRITY CHECK
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            LEDGER HISTORY
          </button>
        </nav>

        {/* Right Blockchain System Telemetry Cluster */}
        <div className="nav-sys-telemetry">
          <div className="telemetry-chip">
            <span className="sys-node-dot" />
            <span className="chip-label">NETWORK:</span>
            <span className="chip-val">Ganache (1337)</span>
          </div>
          <div className="telemetry-chip">
            <span className="chip-label">BLOCK:</span>
            <span className="chip-val accent">#{statusInfo?.latest_block || 1}</span>
          </div>
          <div className="telemetry-chip hide-mobile">
            <span className="chip-label">CONTRACT:</span>
            <span className="chip-val code">{statusInfo?.contract_address ? `${statusInfo.contract_address.slice(0, 6)}...${statusInfo.contract_address.slice(-4)}` : '0xc8C3...E0F0'}</span>
          </div>
          <div className="telemetry-chip hide-mobile">
            <span className="chip-label">ETH:</span>
            <span className="chip-val highlight">{statusInfo?.wallet_balance !== undefined ? `${statusInfo.wallet_balance} ETH` : '999.99 ETH'}</span>
          </div>
        </div>
      </header>

      {/* 2. MAIN CONTENT BODY */}
      <main className="workstation-body">
        {activeTab === 'workstation' && (
          <div className="workstation-hero-layout">
            {/* Left/Main Hero Camera Viewport */}
            <div className="hero-viewport-column">
              <CameraViewport
                mode={mode}
                setMode={setMode}
                customImage={customImage}
                setCustomImage={setCustomImage}
                onCapture={handleCaptureAndRun}
                pipelineState={pipelineState}
                onResetState={handleResetState}
              />
            </div>

            {/* Right Pipeline Telemetry & Results Column */}
            <div className="hero-telemetry-column">
              {/* Process Stepper */}
              <ProcessStageStepper
                currentStage={currentStage}
                pipelineState={pipelineState}
              />

              {/* Match Results or Idle Instruction Card */}
              {pipelineResults ? (
                <MatchResultsCard
                  resultsData={pipelineResults}
                  statusInfo={statusInfo}
                  onReset={handleResetState}
                  onQuickVerify={(recId) => setActiveTab('verification')}
                />
              ) : (
                <div className="idle-instruction-card">
                  <div className="idle-icon">
                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="1.5">
                      <circle cx="12" cy="12" r="10" />
                      <circle cx="12" cy="12" r="3" />
                      <line x1="12" y1="2" x2="12" y2="4" />
                      <line x1="12" y1="20" x2="12" y2="22" />
                      <line x1="2" y1="12" x2="4" y2="12" />
                      <line x1="20" y1="12" x2="22" y2="12" />
                    </svg>
                  </div>
                  <h3>Ready for Face Verification</h3>
                  <p>
                    Position your face in the camera viewport on the left or upload an image file. The system tracks your face using computer vision. Click <strong>CAPTURE FACE & VERIFY</strong> to search the web and notarize on the blockchain.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'verification' && (
          <VerificationView statusInfo={statusInfo} />
        )}

        {activeTab === 'history' && (
          <HistoryView
            onSelectRecordForVerify={(id) => {
              setActiveTab('verification');
            }}
          />
        )}
      </main>
    </div>
  );
}
