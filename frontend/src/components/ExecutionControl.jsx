import React from 'react';
import { ASSETS, DATASETS, SCENARIOS } from '../assets/datasets';

export default function ExecutionControl({
  execMode,
  setExecMode,
  activeScenario,
  onSelectScenario,
  currentKey,
  onSelectDataset
}) {
  return (
    <section className="control-deck-card">
      <div className="control-deck-top">
        <div className="control-heading-wrap">
          <span className="control-heading">Execution Control</span>
          <span className="nav-tag" id="currentExecModeTag">
            {execMode === 'sandbox' ? 'Sandbox Simulator' : 'Live Python API'}
          </span>
        </div>

        <div className="segmented-control">
          <button
            className={`segment-btn ${execMode === 'sandbox' ? 'active' : ''}`}
            onClick={() => setExecMode('sandbox')}
          >
            <span>Sandbox Mode</span>
          </button>
          <button
            className={`segment-btn ${execMode === 'live' ? 'active' : ''}`}
            onClick={() => {
              setExecMode('live');
              alert('Live Python API Selected: Backend server active on http://localhost:8080');
            }}
          >
            <span>Live Python API</span>
          </button>
        </div>
      </div>

      {/* Simulation Scenarios */}
      <div className="section-micro-label">Test Scenarios</div>
      <div className="scenario-grid">
        {SCENARIOS.map(scen => {
          const isActive = activeScenario === scen.id;
          const statusVar = `var(--status-${scen.status})`;
          return (
            <div
              key={scen.id}
              className={`scenario-tile ${isActive ? 'active' : ''}`}
              onClick={() => onSelectScenario(scen.id)}
            >
              <div className="scenario-header-row">
                <span className="scenario-badge" style={{ color: statusVar }}>
                  <span className="scenario-badge-dot" style={{ background: statusVar }}></span>
                  {scen.label}
                </span>
                <span className="scenario-val" style={{ color: statusVar }}>
                  {scen.score}
                </span>
              </div>
              <div className="scenario-note">{scen.note}</div>
            </div>
          );
        })}
      </div>

      {/* Quick Load Test Dataset */}
      <div className="section-micro-label">Test Datasets</div>
      <div className="dataset-grid">
        {DATASETS.map(data => {
          const isActive = currentKey === data.id;
          return (
            <div
              key={data.id}
              className={`dataset-tile ${isActive ? 'active' : ''}`}
              onClick={() => onSelectDataset(data.id)}
            >
              <img
                src={ASSETS[data.id]}
                className="dataset-preview"
                alt={data.name}
              />
              <div className="dataset-meta">
                <div className="dataset-name">{data.name}</div>
                <div className="dataset-sub">{data.sub}</div>
                <div className="dataset-spec">{data.spec}</div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
