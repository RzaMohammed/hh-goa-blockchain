# Biometric Blockchain Verification — Frontend Client

The frontend interface for the **Face Identification & Blockchain Verification Engine (HH Goa 2026)**. Built with React and Vite, it delivers real-time webcam biometric detection, dynamic reverse-image search inspection, cryptographic SHA-256 verification, and on-chain Ethereum smart contract interactions.

---

## Key Features & Tabs

- **Pipeline Execution Tab (`CameraViewport.jsx`, `MatchResultsCard.jsx`)**
  - Live webcam stream with real-time OpenCV YuNet face bounding boxes and facial landmark overlays.
  - Device photo upload and image crop options.
  - Multi-provider reverse search engine inspection (SerpApi, Serper, SearchApi, direct).
  - Cosine similarity ranking against deep learning SFace embeddings.

- **Integrity Verification Tab (`VerificationView.jsx`)**
  - Upload or select previously matched media.
  - Instant client-side & server-side SHA-256 digest recalculation.
  - Live Ganache smart contract query comparing current hash against the immutable on-chain record.

- **On-Chain Ledger Tab (`OnChainLedgerTab.jsx`)**
  - Blockchain explorer view querying recorded identity hashes, timestamps, and origin source URLs from the Solidity contract.

- **Tamper Audit Lab (`TamperAuditLabTab.jsx`)**
  - Interactive demonstration allowing users to flip bytes or alter image pixels.
  - Real-time cryptographic avalanche effect visualization showing how minor mutations invalidate on-chain verification.

- **Architecture Specifications (`ArchitectureSpecsTab.jsx`)**
  - Detailed flow diagrams, cryptographic parameter references, and smart contract ABI inspection.

---

## Directory Structure

```text
frontend/
├── public/              # Static assets and favicon
├── src/
│   ├── assets/          # Dataset samples and icons
│   ├── components/      # Modular React UI views
│   │   ├── CameraViewport.jsx
│   │   ├── MatchResultsCard.jsx
│   │   ├── VerificationView.jsx
│   │   ├── BlockchainDetailsModal.jsx
│   │   ├── OnChainLedgerTab.jsx
│   │   ├── TamperAuditLabTab.jsx
│   │   └── ArchitectureSpecsTab.jsx
│   ├── App.jsx          # Main application container & state management
│   ├── App.css          # App-level styling
│   ├── index.css        # Design system, glassmorphism tokens, and animations
│   └── main.jsx         # React application entry point
├── package.json         # Dependencies & scripts
└── vite.config.js       # Vite build configuration
```

---

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The application will launch on `http://localhost:5173` with Hot Module Replacement (HMR).

### 3. Production Build
```bash
npm run build
```
Generates the optimized static distribution inside `frontend/dist/`.
