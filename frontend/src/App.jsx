import React, { useState } from 'react';
import TopNavbar from './components/TopNavbar';
import ProjectHeader from './components/ProjectHeader';
import ExecutionControl from './components/ExecutionControl';
import NavigationTabs from './components/NavigationTabs';
import BiometricViewport from './components/PipelineExecutionTab/BiometricViewport';
import PipelineStepper from './components/PipelineExecutionTab/PipelineStepper';
import IntegrityVerificationTab from './components/IntegrityVerificationTab';
import TamperAuditLabTab from './components/TamperAuditLabTab';
import OnChainLedgerTab from './components/OnChainLedgerTab';
import ArchitectureSpecsTab from './components/ArchitectureSpecsTab';
import BottomStatusDock from './components/BottomStatusDock';
import { ASSETS, DATASETS } from './assets/datasets';

const INITIAL_STEPS = [
  {
    id: 1,
    title: 'Biometric Facial Alignment',
    meta: 'YuNet DNN • 38ms',
    desc: 'Extracts 5 fiducials (eyes, nose, mouth corners)',
    state: 'pending',
    badge: 'Pending'
  },
  {
    id: 2,
    title: 'Reverse Search Candidate Retrieval',
    meta: 'Lens API • 612ms',
    desc: 'Queries Google Lens candidate index for matching media',
    state: 'pending',
    badge: 'Pending'
  },
  {
    id: 3,
    title: 'Cosine Similarity Ranking',
    meta: 'SFace 512-d • 19ms',
    desc: 'Compares unit vectors against the strict 85% match gate',
    state: 'pending',
    badge: 'Pending'
  },
  {
    id: 4,
    title: 'Cryptographic Checksum',
    meta: 'RFC 8785 • 4ms',
    desc: 'Computes canonical deterministic SHA-256 payload digest',
    state: 'pending',
    badge: 'Pending'
  },
  {
    id: 5,
    title: 'On-Chain Notarization',
    meta: 'SPL Memo • 285ms',
    desc: 'Signs and broadcasts immutable decentralized ledger proof',
    state: 'pending',
    badge: 'Pending'
  }
];

export default function App() {
  // Global State
  const [activeNetwork, setActiveNetwork] = useState('solana'); // 'solana' | 'sepolia'
  const [execMode, setExecMode] = useState('sandbox'); // 'sandbox' | 'live'
  const [activeScenario, setActiveScenario] = useState('verified');
  const [currentKey, setCurrentKey] = useState('person');
  const [currentHash, setCurrentHash] = useState(
    'a7f28c11e3895a98d0f1982b6c934b071295b9c7fa689255627a9446d1e43e2f'
  );
  const [activeTab, setActiveTab] = useState('tab-pipeline');

  // Pipeline Execution State
  const [threshold, setThreshold] = useState(0.85);
  const [searchProvider, setSearchProvider] = useState('direct');
  const [isRunning, setIsRunning] = useState(false);
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [telemetryStatus, setTelemetryStatus] = useState('Ready');
  const [verdict, setVerdict] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [receipt, setReceipt] = useState(null);

  // Network Toggle
  const toggleNetwork = () => {
    setActiveNetwork(prev => (prev === 'solana' ? 'sepolia' : 'solana'));
  };

  // Scenario Selection
  const handleSelectScenario = (scenId) => {
    setActiveScenario(scenId);
    if (scenId === 'verified') {
      handleSelectDataset('person');
    } else if (scenId === 'tampered') {
      handleSelectDataset('tamper');
    } else if (scenId === 'lowmatch') {
      handleSelectDataset('lookalike');
    } else if (scenId === 'noface') {
      handleSelectDataset('noface');
    }
  };

  // Dataset Selection
  const handleSelectDataset = (key) => {
    setCurrentKey(key);
    const found = DATASETS.find(d => d.id === key);
    if (found) {
      setCurrentHash(found.hash);
    }
  };

  // Custom Upload
  const handleCustomUpload = (imgSrc, hash, fileName) => {
    ASSETS.custom = imgSrc;
    setCurrentKey('custom');
    setCurrentHash(hash);
  };

  // Run Pipeline Flow
  const runPipeline = async () => {
    setIsRunning(true);
    setTelemetryStatus('Running...');
    setVerdict(null);
    setCandidates([]);
    setReceipt(null);

    // Reset Steps
    setSteps(INITIAL_STEPS.map(s => ({ ...s, state: 'pending', badge: 'Pending' })));

    const updateStep = (id, state, badge) => {
      setSteps(prev =>
        prev.map(s => (s.id === id ? { ...s, state, badge } : s))
      );
    };

    const sleep = (ms) => new Promise(r => setTimeout(r, ms));

    // Check for No Face
    if (currentKey === 'noface' || activeScenario === 'noface') {
      updateStep(1, 'active', 'Detecting...');
      await sleep(400);
      updateStep(1, 'failed', '0 Faces Detected');
      setTelemetryStatus('Halted');
      setVerdict({
        type: 'noface',
        title: 'Stage 1 Halted: No Face Detected',
        message: 'YuNet detector found zero human faces in the provided frame. Reverse search and on-chain notarization were skipped.'
      });
      setIsRunning(false);
      return;
    }

    // Step 1: Face Alignment
    updateStep(1, 'active', 'Extracting...');
    await sleep(350);
    updateStep(1, 'completed', 'Aligned (5 Fiducials)');

    // Step 2: Reverse Search
    updateStep(2, 'active', 'Querying Google Lens...');
    await sleep(600);
    updateStep(2, 'completed', '3 Candidates Discovered');

    // Step 3: Cosine Similarity
    updateStep(3, 'active', 'Evaluating Vectors...');
    await sleep(400);

    const isTamper = activeScenario === 'tampered';
    const isLow = activeScenario === 'lowmatch';
    const scoreLabel = isLow
      ? '68.2% (Below Gate)'
      : isTamper
      ? '94.8% (Altered)'
      : '94.8% (Verified)';

    updateStep(3, 'completed', scoreLabel);

    // Set Candidates
    if (isLow) {
      setCandidates([
        {
          avatar: ASSETS.lookalike,
          label: 'Lookalike Match (Web Article)',
          link: 'https://wikimedia.org/wiki/File:Portrait_Distant.jpg',
          score: 68.2,
          color: 'var(--status-lowmatch)',
          tag: 'Low Match',
          tagColor: 'var(--status-lowmatch)'
        }
      ]);
      updateStep(4, 'failed', 'Skipped');
      updateStep(5, 'failed', 'Skipped (Below Threshold)');
      setTelemetryStatus('Rejected');
      setVerdict({
        type: 'lowmatch',
        title: 'Low Similarity: Verification Rejected',
        message: 'The candidate portrait cosine similarity of 68.2% is below the required 85.0% threshold gate. Proof not notarized.'
      });
      setIsRunning(false);
      return;
    }

    setCandidates([
      {
        avatar: ASSETS.tamper,
        label: 'Speaker Profile Header (Summit CDN)',
        link: 'https://images.unsplash.com/photo-tech-speaker',
        score: 94.8,
        color: 'var(--status-verified)',
        tag: 'Verified',
        tagColor: 'var(--status-verified)',
        isBest: true
      },
      {
        avatar: ASSETS.lookalike,
        label: 'Conference Attendee Photo',
        link: 'https://wikimedia.org/wiki/File:Attendee_Photo.jpg',
        score: 42.1,
        color: 'var(--text-muted)',
        tag: 'Rejected',
        opacity: 0.5
      }
    ]);

    // Step 4: Cryptographic Hashing
    updateStep(4, 'active', 'Computing SHA-256...');
    await sleep(300);
    updateStep(4, 'completed', `SHA-256: ${currentHash.substring(0, 16)}...`);

    // Step 5: On-Chain Notarization
    const netLabel =
      activeNetwork === 'solana'
        ? 'Solana Devnet (SPL Memo)'
        : 'Ethereum Sepolia (Solidity)';
    updateStep(5, 'active', `Notarizing on ${netLabel}...`);
    await sleep(700);
    updateStep(5, 'completed', 'Confirmed On-Chain');

    // Populate Receipt
    const txSig =
      activeNetwork === 'solana'
        ? '4uQ9wF3x7bXk2mKp9P4rY8zQ1vA5cB6dE7fG8hJ9kL0'
        : '0x7e8b91a0c4f8d23e57b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3';

    const explorerUrl =
      activeNetwork === 'solana'
        ? `https://explorer.solana.com/tx/${txSig}?cluster=devnet`
        : `https://sepolia.etherscan.io/tx/${txSig}`;

    setReceipt({
      network: netLabel,
      txSig,
      sha256: isTamper
        ? '3d99e526c7104b281f62b78b88df14299b8214fa39062dc962ceb33d0e2c8841 (Tampered)'
        : currentHash,
      score: '94.8% Match',
      slotState: 'Finalized (Slot #291,048,122)',
      latency: '958ms (End-to-End)',
      explorerUrl
    });

    if (isTamper) {
      setTelemetryStatus('Tamper Detected');
      setVerdict({
        type: 'tampered',
        title: 'Audit X: Cryptographic Tamper Detected',
        message: 'Local media bytes differ from the on-chain notarized hash! Checksum mismatch indicates payload was modified post-notarization.'
      });
    } else {
      setTelemetryStatus('Notarized & Verified');
      setVerdict({
        type: 'verified',
        title: 'On-Chain Verification Passed',
        message: '100% Cryptographic Match! The portrait has been authenticated, SHA-256 validated, and notarized to the decentralized ledger.'
      });
    }

    setIsRunning(false);
  };

  const handleQuickVerify = (id) => {
    setActiveTab('tab-verify');
  };

  return (
    <div className="dashboard-layout">
      {/* 1. TOP NAVBAR */}
      <TopNavbar activeNetwork={activeNetwork} toggleNetwork={toggleNetwork} />

      {/* 2. PROJECT HEADER */}
      <ProjectHeader />

      {/* 3. EXECUTION CONTROL */}
      <ExecutionControl
        execMode={execMode}
        setExecMode={setExecMode}
        activeScenario={activeScenario}
        onSelectScenario={handleSelectScenario}
        currentKey={currentKey}
        onSelectDataset={handleSelectDataset}
      />

      {/* 4. NAVIGATION TABS */}
      <NavigationTabs activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* TAB 1: PIPELINE EXECUTION */}
      <div className={`tab-view ${activeTab === 'tab-pipeline' ? 'active' : ''}`}>
        <div className="dashboard-grid">
          <BiometricViewport
            currentKey={currentKey}
            onCustomUpload={handleCustomUpload}
            threshold={threshold}
            setThreshold={setThreshold}
            searchProvider={searchProvider}
            setSearchProvider={setSearchProvider}
            onRunPipeline={runPipeline}
            isRunning={isRunning}
          />
          <PipelineStepper
            steps={steps}
            telemetryStatus={telemetryStatus}
            verdict={verdict}
            candidates={candidates}
            receipt={receipt}
            activeNetwork={activeNetwork}
          />
        </div>
      </div>

      {/* TAB 2: INTEGRITY VERIFICATION */}
      <div className={`tab-view ${activeTab === 'tab-verify' ? 'active' : ''}`}>
        <IntegrityVerificationTab />
      </div>

      {/* TAB 3: TAMPER AUDIT LAB */}
      <div className={`tab-view ${activeTab === 'tab-tamper' ? 'active' : ''}`}>
        <TamperAuditLabTab />
      </div>

      {/* TAB 4: ON-CHAIN LEDGER */}
      <div className={`tab-view ${activeTab === 'tab-ledger' ? 'active' : ''}`}>
        <OnChainLedgerTab onQuickVerify={handleQuickVerify} />
      </div>

      {/* TAB 5: ARCHITECTURE & SPECS */}
      <div className={`tab-view ${activeTab === 'tab-specs' ? 'active' : ''}`}>
        <ArchitectureSpecsTab />
      </div>

      {/* 5. BOTTOM STATUS DOCK */}
      <BottomStatusDock
        activeNetwork={activeNetwork}
        onOpenSpecs={() => setActiveTab('tab-specs')}
      />
    </div>
  );
}
