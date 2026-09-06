import React from 'react';

export default function ProcessStageStepper({ currentStage, pipelineState }) {
  const stages = [
    { id: 1, label: 'FACE', name: 'Face Detection' },
    { id: 2, label: 'SEARCH', name: 'Web Search' },
    { id: 3, label: 'MATCH', name: 'Similarity' },
    { id: 4, label: 'FINGERPRINT', name: 'SHA-256 Hash' },
    { id: 5, label: 'BLOCKCHAIN', name: 'On-Chain Ledger' }
  ];

  const getStageStatus = (stageId) => {
    if (pipelineState === 'failed' && currentStage === stageId) return 'failed';
    if (currentStage > stageId) return 'completed';
    if (currentStage === stageId) return 'active';
    return 'pending';
  };

  return (
    <div className="process-stepper-bar">
      {stages.map((stg, idx) => {
        const status = getStageStatus(stg.id);
        return (
          <React.Fragment key={stg.id}>
            <div className={`stepper-node ${status}`}>
              <div className="node-icon">
                {status === 'completed' ? (
                  '✓'
                ) : status === 'failed' ? (
                  '✕'
                ) : status === 'active' ? (
                  <span className="pulse-dot-inline" />
                ) : (
                  stg.id
                )}
              </div>
              <div className="node-meta">
                <span className="node-label">{stg.label}</span>
                <span className="node-sub">{stg.name}</span>
              </div>
            </div>
            {idx < stages.length - 1 && (
              <div className={`stepper-connector ${currentStage > stg.id ? 'active' : ''}`} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
