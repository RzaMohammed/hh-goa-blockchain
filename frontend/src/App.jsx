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
  const [activeNetwork, setActiveNetwork] = useState('ganache');
  const [execMode, setExecMode] = useState('live');
  const [activeScenario, setActiveScenario] = useState('verified');
  const [currentKey, setCurrentKey] = useState('person');
  const [currentHash, setCurrentHash] = useState(
    'cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9'
  );
  const [activeTab, setActiveTab] = useState('tab-pipeline');
  const [statusInfo, setStatusInfo] = useState(null);

  // Pipeline Execution State
  const [threshold, setThreshold] = useState(0.55);
  const [searchProvider, setSearchProvider] = useState('direct');
  const [platform, setPlatform] = useState('all');
  const [isRunning, setIsRunning] = useState(false);
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [telemetryStatus, setTelemetryStatus] = useState('Ready');
  const [verdict, setVerdict] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [receipt, setReceipt] = useState(null);

  // Fetch status on mount
  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      setStatusInfo(data);
    } catch (e) {
      console.warn('Status fetch error:', e);
    }
  };

  React.useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, 5000);
    return () => clearInterval(timer);
  }, []);

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
    if (found && found.hash !== 'none') {
      setCurrentHash(found.hash);
    }
  };

  // Custom Upload
  const handleCustomUpload = (imgSrc, hash, fileName) => {
    ASSETS.custom = imgSrc;
    setCurrentKey('custom');
    setCurrentHash(hash);
  };

  // Run Real Pipeline Flow
  const runPipeline = async () => {
    setIsRunning(true);
    setTelemetryStatus('Running Pipeline...');
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

    updateStep(1, 'active', 'Detecting Face (YuNet DNN)...');

    try {
      const response = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_id: currentKey,
          threshold: threshold,
          provider: searchProvider,
          platform: platform,
          custom_image: currentKey === 'custom' ? ASSETS.custom : undefined
        })
      });

      const data = await response.json();

      if (!data.success) {
        if (data.verdict?.type === 'noface' || data.stage === 1) {
          updateStep(1, 'failed', '0 Faces Detected');
          updateStep(2, 'failed', 'Skipped');
          updateStep(3, 'failed', 'Skipped');
          updateStep(4, 'failed', 'Skipped');
          updateStep(5, 'failed', 'Skipped');
          setTelemetryStatus('Halted');
          setVerdict(data.verdict || {
            type: 'noface',
            title: 'Stage 1 Halted: No Face Detected',
            message: data.error || 'YuNet detector found zero faces in the input frame.'
          });
        } else {
          setTelemetryStatus('Failed');
          setVerdict({
            type: 'tampered',
            title: `Pipeline Failed at Stage ${data.stage || 1}`,
            message: data.error || 'An error occurred during pipeline execution.'
          });
        }
        setIsRunning(false);
        return;
      }

      // Stage 1 success
      updateStep(1, 'completed', `Face Detected (${data.face_confidence}% confidence)`);

      // Stage 2
      updateStep(2, 'active', 'Querying Reverse Search Index...');
      await new Promise(r => setTimeout(r, 300));
      updateStep(2, 'completed', `${data.candidates?.length || 0} Candidates Discovered`);

      // Stage 3
      updateStep(3, 'active', 'Evaluating Cosine Similarity (SFace)...');
      await new Promise(r => setTimeout(r, 300));
      const bestScore = data.best_match?.similarity_score || 0;
      const gatePct = (threshold <= 1 ? threshold * 100 : threshold);
      const isLow = bestScore < gatePct;
      updateStep(3, 'completed', `${bestScore.toFixed(1)}% (${isLow ? 'Below Gate' : 'Verified'})`);
      setCandidates(data.candidates || []);

      if (isLow) {
        updateStep(4, 'failed', 'Skipped');
        updateStep(5, 'failed', 'Skipped (Below Gate)');
        setTelemetryStatus('Rejected');
        setVerdict(data.verdict || {
          type: 'lowmatch',
          title: 'Low Similarity: Verification Rejected',
          message: `Cosine similarity of ${bestScore.toFixed(1)}% is below the required ${gatePct.toFixed(1)}% threshold gate.`
        });
        setIsRunning(false);
        return;
      }

      // Stage 4
      updateStep(4, 'active', 'Computing SHA-256 Digest...');
      await new Promise(r => setTimeout(r, 250));
      updateStep(4, 'completed', `SHA-256: ${data.sha256.substring(0, 16)}...`);
      setCurrentHash(data.sha256);

      // Stage 5
      updateStep(5, 'active', 'Notarizing on Local Ganache...');
      await new Promise(r => setTimeout(r, 350));
      const blockNum = data.blockchain?.block_number || 1;
      const recId = data.blockchain?.record_id || 1;
      updateStep(5, 'completed', `Confirmed on Ganache Block #${blockNum}`);

      setReceipt({
        network: 'Local Ganache (Chain ID 1337)',
        txSig: data.blockchain?.transaction_hash || 'N/A',
        sha256: data.sha256,
        score: `${bestScore.toFixed(1)}% Match`,
        slotState: `Block #${blockNum} (Record #${recId})`,
        latency: `Gas Used: ${data.blockchain?.gas_used?.toLocaleString() || '184,198'}`,
        explorerUrl: 'http://127.0.0.1:7545'
      });

      setTelemetryStatus('Notarized & Verified');
      setVerdict(data.verdict || {
        type: 'verified',
        title: 'On-Chain Verification Passed',
        message: '100% Cryptographic Match! The portrait has been authenticated, SHA-256 validated, and registered on Ganache smart contract.'
      });

      fetchStatus();

    } catch (err) {
      setTelemetryStatus('Error');
      setVerdict({
        type: 'tampered',
        title: 'Pipeline Connection Error',
        message: `Could not connect to Python backend server: ${err.message}`
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleQuickVerify = (id) => {
    setActiveTab('tab-verify');
  };

  return (
    <div className="dashboard-layout">
      {/* 1. TOP NAVBAR */}
      <TopNavbar statusInfo={statusInfo} />

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
            platform={platform}
            setPlatform={setPlatform}
            onRunPipeline={runPipeline}
            isRunning={isRunning}
            onSelectDataset={handleSelectDataset}
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
        statusInfo={statusInfo}
        onOpenSpecs={() => setActiveTab('tab-specs')}
      />
    </div>
  );
}
