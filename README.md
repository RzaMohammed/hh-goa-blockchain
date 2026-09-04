# Face Identification & Blockchain Verification

**HH Goa 2026 Shortlisting Task 3: Complete End-to-End Command-Line Pipeline**

An automated, tamper-evident media verification pipeline that takes an input face photograph, dynamically performs genuine reverse-image web searching to discover candidate web/social-media content, ranks candidates using deep learning facial similarity embeddings, downloads the matching image, calculates its cryptographic SHA-256 fingerprint, records that fingerprint on the **Ethereum Sepolia** blockchain via a Solidity smart contract, and provides an independent verification flow to mathematically prove whether local media has been altered or tampered with.

---

## Architecture Diagram

```text
========================================================================================
                               PIPELINE ARCHITECTURE
========================================================================================

 [1] INPUT IMAGE
        │  (e.g., input/person.jpg)
        ▼
 [2] FACE DETECTION & LANDMARK ALIGNMENT (OpenCV YuNet DNN)
        │  - Detects bounding box & 5 facial landmarks (eyes, nose, mouth)
        │  - Handles multi-face scenarios (selects primary subject)
        │  - Gracefully handles no-face error
        ▼
 [3] 128-DIMENSIONAL EMBEDDING (OpenCV SFace DNN)
        │  - Aligns and crops facial region
        │  - Generates 128-d deep feature vector
        ▼
 [4] GENUINE WEB REVERSE IMAGE SEARCH (Modular Search Providers)
        │  - SerpApi (Google Lens engine) / Serper.dev / Openverse Web
        │  - Dynamically discovers real candidate web / social-media URLs
        ▼
 [5] CANDIDATE MATCHING & SIMILARITY COMPARISON
        │  - Downloads accessible candidate images over HTTP
        │  - Extracts candidate face embeddings
        │  - Computes Cosine Similarity & evaluates against threshold
        │  - Identifies BEST MATCH (highest similarity)
        ▼
 [6] CONTENT ACQUISITION & CRYPTOGRAPHIC FINGERPRINTING
        │  - Saves matched image to output/matched_image.jpg
        │  - Calculates SHA-256 hash from raw file bytes
        │  - Prepares bytes32 cryptographic digest
        ▼
 [7] ETHEREUM SEPOLIA BLOCKCHAIN REGISTRATION
        │  - Connects to Sepolia via Web3.py RPC
        │  - Signs transaction with wallet private key
        │  - Invokes Solidity Smart Contract: registerRecord(bytes32, url)
        │  - Confirms transaction on-chain & saves output/result.json
        ▼
 ========================================================================================
                         LATER VERIFICATION / TAMPER DETECTION
 ========================================================================================

 Current Local File (output/matched_image.jpg) ─────────► Compute SHA-256 Hash
                                                                  │
                                                                  ▼
 Ethereum Sepolia Smart Contract ───────────────────────► Retrieve On-Chain Hash
                                                                  │
                                                                  ▼
                                                       Compare Both Hashes
                                                       ┌──────────┴──────────┐
                                                       ▼                     ▼
                                                 [HASH MATCH]         [HASH MISMATCH]
                                                       │                     │
                                                       ▼                     ▼
                                               VERIFICATION PASSED   VERIFICATION FAILED
                                               (Content Unaltered)   (Content Tampered)
========================================================================================
```

---

## Technologies Used

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Language & Runtime** | Python 3.11+ | Core pipeline orchestration and CLI interface |
| **Face Detection** | OpenCV DNN YuNet | High-speed, high-accuracy face & 5-point landmark detector |
| **Face Embeddings** | OpenCV DNN SFace | 128-dimensional deep metric learning embedding extractor |
| **Web Reverse Search** | SerpApi / Serper / Openverse | Modular dynamic discovery of real web and social content |
| **Fingerprinting** | SHA-256 (`hashlib`) | Cryptographic checksum computed directly from raw file bytes |
| **Smart Contract** | Solidity (`^0.8.20`) | Immutable data ledger storing `(bytes32 dataHash, string sourceUrl, uint256 timestamp, address submitter)` |
| **Blockchain Client** | Web3.py | Transaction construction, EIP-1559 gas calculation, signing, and contract RPC communication |
| **Network** | Ethereum Sepolia Testnet | Public decentralized blockchain testnet (Chain ID: `11155111`) |

---

## How It Works

1. **Face Detection**: Loads the input photograph. Uses OpenCV's deep neural network (`cv2.FaceDetectorYN`) to detect faces and extract five facial landmarks (right eye, left eye, nose tip, right mouth corner, left mouth corner). If multiple individuals appear in the image, the primary face is selected by bounding-box area, and a warning is logged.
2. **Face Encoding**: The detected face is aligned and cropped using its landmarks, then passed through OpenCV's SFace deep recognition model (`cv2.FaceRecognizerSF`) to produce a 128-dimensional unit feature vector.
3. **Reverse Web Search**: The image is queried against reverse-image search providers (SerpApi Google Lens, Serper.dev, or Openverse live discovery). This dynamically retrieves real web and social URLs where candidate matching images reside.
4. **Candidate Matching**: Candidate images are safely downloaded over HTTP, validated for image format, and processed through the face detector and recognizer. The Cosine Similarity between the query face and each candidate face is computed and converted to a similarity score. Candidates are ranked descending, and the highest scoring candidate is selected subject to a configurable similarity threshold.
5. **Content Download**: The discovered matching image is saved to `output/matched_image.jpg`.
6. **SHA-256 Hashing**: A cryptographic SHA-256 fingerprint is calculated across the raw file bytes of `matched_image.jpg`.
7. **Blockchain Registration**: The SHA-256 hex string is converted to a 32-byte representation (`bytes32`) and recorded on the **Ethereum Sepolia** blockchain by sending a signed transaction to the `FaceVerification` smart contract. A transaction receipt is generated, confirming block number, gas used, submitter address, and record ID. Full metadata is saved to `output/result.json`.
8. **Later Verification**: At any subsequent point, the user runs `verify.py`. The local file is hashed again and compared against the immutable hash retrieved from the Ethereum Sepolia smart contract. If the hashes match, verification passes. If even a single byte has been modified, the hashes differ and tamper detection triggers immediately.

---

## Blockchain Explanation

* **Ethereum**: A decentralized, world-wide state machine secured by cryptographic consensus across thousands of independent nodes.
* **Sepolia Testnet**: The official Ethereum proof-of-stake test network (Chain ID `11155111`), providing a real EVM environment identical to Ethereum mainnet without real financial costs.
* **Smart Contracts**: Autonomous, immutable programs deployed directly to the blockchain. Our contract (`FaceVerification`) stores the cryptographic fingerprint, source URL, submission timestamp, and the submitter's wallet address.
* **Transactions & Gas**: Every write to Ethereum requires a signed cryptographic transaction paid with gas (measured in Gwei). Transactions are confirmed in blocks and cannot be reverted or overwritten.
* **Wallets & Keys**: The submitter uses an Ethereum private key to digitally sign transactions. The contract automatically logs `msg.sender` as the submitter.
* **Why Blockchain Proves Tamper-Evidence**:
  - The blockchain provides **immutability**. Once a transaction is mined into a block, neither the creator, the hosting provider, nor an attacker can alter the recorded hash.
  - The blockchain provides **trusted timestamping**. The block timestamp is set by network consensus when the transaction is mined.
  - The blockchain record **does not store the image bytes directly** (which would be prohibitively expensive in gas), but rather stores its cryptographic digest (`bytes32`). Any modification of the image file produces an avalanche effect in SHA-256, immediately exposing the discrepancy upon verification.

---

## Installation (Windows / PowerShell)

### Prerequisites
* Python 3.11 or higher installed on your system.
* PowerShell execution policy allowing virtual environment activation.

### Step 1: Open PowerShell and Navigate to Project
```powershell
cd "c:\dev\hh goa blockchain"
```

### Step 2: Set Up Virtual Environment
```powershell
python -m venv .venv
```

If PowerShell blocks script execution, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```
Then activate the environment:
```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

> **Note**: ONNX deep learning models (`YuNet` and `SFace`) are automatically downloaded to `models/` on the first run. No C++ compiler or CMake is required.

---

## Environment Configuration (`.env`)

Copy the example configuration file:
```powershell
Copy-Item .env.example .env
```

Open `.env` in a text editor and fill in your credentials:

```env
# Ethereum Sepolia RPC URL
RPC_URL=https://ethereum-sepolia-rpc.publicnode.com

# Ethereum Sepolia Wallet Private Key (Do NOT share or commit!)
PRIVATE_KEY=0x_your_private_key_here

# Deployed Smart Contract Address (populated automatically by deploy.py)
CONTRACT_ADDRESS=

# Reverse Search API Keys (Optional, provides Google Lens reverse search)
SERPAPI_API_KEY=your_serpapi_key_here
SERPER_API_KEY=your_serper_key_here
DEFAULT_SEARCH_PROVIDER=direct

# Pipeline Parameters
SIMILARITY_THRESHOLD=0.55
OUTPUT_DIR=output
```

### How to Obtain Free Sepolia Test ETH
To deploy the contract and register hashes on Sepolia, your wallet needs a small amount of test ETH:
1. **Google Cloud Web3 Faucet**: [https://cloud.google.com/application/web3/faucet/ethereum/sepolia](https://cloud.google.com/application/web3/faucet/ethereum/sepolia) (instant, no signup)
2. **Chainlink Faucet**: [https://faucets.chain.link/](https://faucets.chain.link/)
3. **Alchemy Sepolia Faucet**: [https://www.alchemy.com/faucets/ethereum-sepolia](https://www.alchemy.com/faucets/ethereum-sepolia)
4. **Sepolia PoW Faucet**: [https://sepolia-faucet.pk910.de/](https://sepolia-faucet.pk910.de/)

---

## Smart Contract Deployment

Once your wallet has Sepolia test ETH, deploy the contract with a single command:

```powershell
python blockchain/deploy.py
```

### Output:
```text
============================================================
  ETHEREUM SEPOLIA - CONTRACT DEPLOYMENT
============================================================

[1] Deployer Wallet: 0xYourWalletAddress...
[2] Connecting to RPC: https://ethereum-sepolia-rpc.publicnode.com
[3] Network: Ethereum Sepolia (Testnet)
[4] Wallet Balance: 0.25000 ETH
[5] Compiling and loading contract artifacts...
[6] Building deployment transaction...
[7] Signing transaction with private key...
[8] Sending transaction to Ethereum Sepolia...
    Transaction Hash: 0x...
    Waiting for block confirmation on-chain...

============================================================
  CONTRACT DEPLOYED SUCCESSFULLY!
============================================================
Contract Address: 0xYourContractAddress...
Transaction:      0x...
Block Number:     11634620
Gas Used:         342150
============================================================

[INFO] Updated CONTRACT_ADDRESS in .env
```
`deploy.py` automatically updates `CONTRACT_ADDRESS` in your `.env` file.

---

## Running the Pipeline

### 1. Full Discovery & Registration Pipeline
Run the complete pipeline on an input face image:

```powershell
python app.py --image input/person.jpg
```

**Options:**
* `--image, -i`: Path to input face image (required).
* `--threshold, -t`: Minimum similarity score threshold (default: `0.55`).
* `--provider, -p`: Search provider (`serpapi`, `serper`, `searchapi`, or `direct`).
* `--max-candidates, -m`: Number of candidate results to discover (default: `10`).
* `--local-evm`: Use local in-memory EVM testnet (ideal for offline testing or instant evaluation).
* `--skip-blockchain`: Skip on-chain write (dry run).

### 2. Verifying Media Integrity
Verify whether the downloaded content matches the on-chain record:

```powershell
python verify.py --image output/matched_image.jpg --record 1
```

If the file is unaltered:
```text
============================================================
 BLOCKCHAIN VERIFICATION
 Tamper-Evidence & Integrity Check
============================================================

Target File: output/matched_image.jpg
Record ID:   1

Calculating SHA-256 hash of current local file...
Connecting to Ethereum Sepolia smart contract...
Connected to Contract: 0x...
On-chain Record Timestamp: 2026-09-04 16:36:55 UTC
Discovered Source URL:      https://...
Registered By Wallet:       0x...

------------------------------------------------------------
Blockchain hash:
cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9

Current file hash:
cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9
------------------------------------------------------------

✓ HASH MATCH

✓ VERIFICATION PASSED
The current file matches the fingerprint
recorded on the Ethereum Sepolia blockchain.
File integrity is verified and tamper-free.
```

---

## Tampering Demonstration Procedure

To demonstrate tamper-evidence during an evaluation or screen recording:

### Step 1: Run Registration
```powershell
python app.py --image input/person.jpg --threshold 0.55
```

### Step 2: Verify Initial Integrity (Passed)
```powershell
python verify.py --image output/matched_image.jpg --record 1
```
*Expected Output:* `✓ VERIFICATION PASSED`

### Step 3: Tamper with the Image
Use the included helper to subtly alter the image file:
```powershell
python tamper_demo.py --image output/matched_image.jpg
```

### Step 4: Run Verification Again (Failed / Tampered)
```powershell
python verify.py --image output/matched_image.jpg --record 1
```
*Expected Output:*
```text
------------------------------------------------------------
Blockchain hash:
cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9

Current file hash:
29d0b4cf56dd49adfc63e13cf5eae47fc7afdbff62be39a3694fb230fb05ce18
------------------------------------------------------------

✗ HASH MISMATCH

✗ VERIFICATION FAILED
The current file differs from the recorded version.
The content has been modified, tampered with, or corrupted since registration.
```

### Step 5: Restore Original Image
```powershell
python tamper_demo.py --image output/matched_image.jpg --restore
python verify.py --image output/matched_image.jpg --record 1
```
*Expected Output:* `✓ VERIFICATION PASSED`

---

## Automated Test Suite

Run the full automated test suite covering face detection, similarity matching, SHA-256 fingerprinting, tamper detection, and EVM smart contract logic:

```powershell
pytest -v
```

All 11 unit tests execute in under 3 seconds using local Py-EVM simulation.

---

## Limitations & Ethical Considerations

1. **Reverse-Image Search Constraints**: Commercial search engines (such as Google Lens via SerpApi/Serper) impose rate limits, API quotas, and CAPTCHAs. Open web search providers depend on publicly indexed media.
2. **Access Restrictions & Anti-Bot Protections**: Certain social-media platforms (such as Instagram or private Facebook groups) require authentication or block automated scraping, preventing direct HTTP downloading.
3. **Face Recognition Accuracy & Nuance**:
   - Deep learning face recognition models output probabilistic similarity scores, not mathematical identity proofs.
   - Significant pose variations, heavy occlusions, extreme lighting, or low image resolution can decrease similarity scores (false negatives).
   - Look-alikes, identical twins, or closely related family members may generate elevated similarity scores (false positives).
4. **Image Transformations**: Re-saving an image in JPEG with differing compression parameters or stripping EXIF tags alters file bytes, producing a different SHA-256 hash even if the visual appearance remains unchanged.
5. **Blockchain Scope**:
   - The blockchain guarantees **data integrity and tamper-evidence** (proving that the verified file is identical down to the byte to what was downloaded at registration time).
   - The blockchain **does not prove that the discovered content was truthful, authentic, or unedited prior to download**.
   - A cryptographic hash verifies **file integrity**, not human identity.
6. **Privacy Considerations**: Face recognition technologies involve biometric information. The pipeline processes embeddings locally in memory and registers only the cryptographic fingerprint (`bytes32`) and source URL on-chain, preventing raw facial biometrics from being exposed publicly.
