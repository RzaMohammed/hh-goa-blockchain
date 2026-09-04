# Face Identification & Blockchain Verification

**HH Goa 2026 Shortlisting Task 3: Complete End-to-End Command-Line Pipeline**

An automated, tamper-evident media verification pipeline that takes an input face photograph, dynamically performs genuine reverse-image web searching to discover candidate web/social-media content, ranks candidates using deep learning facial similarity embeddings, downloads the matching image, calculates its cryptographic SHA-256 fingerprint, records that fingerprint on a **Local Ethereum-Compatible Blockchain (Ganache)** via a Solidity smart contract, and provides an independent verification flow to mathematically prove whether local media has been altered or tampered with.

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
        │  - Calculates SHA-256 hash from raw file bytes (Image SHA-256)
        │  - Prepares bytes32 cryptographic digest
        ▼
 [7] LOCAL ETHEREUM BLOCKCHAIN (GANACHE) REGISTRATION
        │  - Connects to Ganache RPC (e.g., http://127.0.0.1:7545)
        │  - Signs transaction using local Ganache development account private key
        │  - Invokes Solidity Smart Contract: registerRecord(bytes32, url)
        │  - Mines transaction on-chain & saves output/result.json
        ▼
 ========================================================================================
                         LATER VERIFICATION / TAMPER DETECTION
 ========================================================================================

 Current Local File (output/matched_image.jpg) ─────────► Compute Current SHA-256 Hash
                                                                  │
                                                                  ▼
 Local Ganache Smart Contract ──────────────────────────► Retrieve On-Chain Hash
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
| **Blockchain Client** | Web3.py | Transaction construction, gas calculation, signing, and contract RPC communication |
| **Blockchain Engine** | Ganache (Local Ethereum) | Local Ethereum-compatible blockchain with real blocks, transactions, and EVM opcodes |

---

## How It Works

1. **Face Detection**: Loads the input photograph. Uses OpenCV's deep neural network (`cv2.FaceDetectorYN`) to detect faces and extract five facial landmarks (right eye, left eye, nose tip, right mouth corner, left mouth corner). If multiple individuals appear in the image, the primary face is selected by bounding-box area, and a warning is logged.
2. **Face Encoding**: The detected face is aligned and cropped using its landmarks, then passed through OpenCV's SFace deep recognition model (`cv2.FaceRecognizerSF`) to produce a 128-dimensional unit feature vector.
3. **Reverse Web Search**: The image is queried against reverse-image search providers (SerpApi Google Lens, Serper.dev, or Openverse live discovery). This dynamically retrieves real web and social URLs where candidate matching images reside.
4. **Candidate Matching**: Candidate images are safely downloaded over HTTP, validated for image format, and processed through the face detector and recognizer. The Cosine Similarity between the query face and each candidate face is computed and converted to a similarity score. Candidates are ranked descending, and the highest scoring candidate is selected subject to a configurable similarity threshold.
5. **Content Download**: The discovered matching image is saved to `output/matched_image.jpg`.
6. **SHA-256 Hashing**: A cryptographic SHA-256 fingerprint is calculated across the raw file bytes of `matched_image.jpg`. Note that the **Image SHA-256** is the content's cryptographic fingerprint, distinctly separated from the **Blockchain Transaction Hash**.
7. **Local Blockchain Registration**: The SHA-256 hex string is converted to a 32-byte representation (`bytes32`) and recorded on the **Local Ganache Blockchain** by sending a signed transaction to the `FaceVerification` smart contract. A real transaction receipt is generated, confirming block number, gas used, submitter address, and record ID. Full metadata is saved to `output/result.json`.
8. **Later Verification**: At any subsequent point, the user runs `verify.py`. The local file is hashed again and compared against the immutable hash retrieved from the smart contract on the local Ganache blockchain. If the hashes match, verification passes. If even a single byte has been modified, the hashes differ and tamper detection triggers immediately.

---

## Ganache — Local Ethereum Blockchain

* **Ganache**: A personal, local Ethereum-compatible blockchain used for development and local testing.
* **Local RPC Endpoint**: Typically runs on `http://127.0.0.1:7545` (Ganache UI) or `http://127.0.0.1:8545` (Ganache CLI).
* **Pre-Funded Development Accounts**: Ganache automatically initializes with pre-funded accounts (typically 100 or 1000 ETH each), eliminating the need for testnet faucets or third-party RPC providers.
* **Smart Contracts on Ganache**: The Solidity smart contract (`FaceVerification`) is deployed directly to Ganache EVM, executing true Ethereum bytecode, mining real blocks, and generating valid transaction hashes.
* **Cryptographic Verification**:
  - The local blockchain acts as an immutable state ledger on your machine.
  - The blockchain stores the file's cryptographic fingerprint (`bytes32`), NOT the image file itself.
  - Any edit to the image file alters its SHA-256 hash, immediately demonstrating tamper evidence upon verification.

---

## Installation (Windows / PowerShell)

### Prerequisites
* Python 3.11 or higher installed on your system.
* Node.js / npx installed (to run Ganache CLI) OR the Ganache UI desktop app.
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

## Setting Up and Starting Ganache

You can run Ganache using either method:

### Option A: Ganache CLI (via npx, Recommended)
In a separate terminal window, start Ganache on port `7545`:

```powershell
npx --yes ganache --port 7545
```

You will see available accounts and their private keys printed in the terminal:
```text
Available Accounts
==================
(0) 0x14ef5fff19927974e58E6a6d7B15bD68499CEB8F (1000 ETH)
...

Private Keys
==================
(0) 0x362f59032e991f49161c7ddf6230f8ff721bf313c269f8f86b3cabc0c758fb2f
...

RPC Listening on 127.0.0.1:7545
```

### Option B: Ganache UI Desktop App
1. Download and open **Ganache UI** from [https://trufflesuite.com/ganache/](https://trufflesuite.com/ganache/).
2. Click **Quickstart Ethereum**.
3. Ensure the RPC server is listening on `HTTP://127.0.0.1:7545`.
4. Click the key icon next to the first account to reveal its private key.

---

## Environment Configuration (`.env`)

Copy the example configuration file:
```powershell
Copy-Item .env.example .env
```

Open `.env` in a text editor and configure your local settings:

```env
# Local Ethereum Blockchain (Ganache) RPC URL
LOCAL_RPC_URL=http://127.0.0.1:7545

# Local Ganache Wallet Private Key (from account 0 above)
LOCAL_PRIVATE_KEY=0x362f59032e991f49161c7ddf6230f8ff721bf313c269f8f86b3cabc0c758fb2f

# Deployed Smart Contract Address (populated automatically by deploy.py)
CONTRACT_ADDRESS=

# Reverse Search API Keys (Optional, provides Google Lens reverse search)
SERPAPI_API_KEY=
SERPER_API_KEY=
DEFAULT_SEARCH_PROVIDER=direct

# Pipeline Parameters
SIMILARITY_THRESHOLD=0.55
OUTPUT_DIR=output
```

---

## Smart Contract Deployment

With Ganache running and `LOCAL_PRIVATE_KEY` set in `.env`, deploy the smart contract to your local blockchain:

```powershell
python blockchain/deploy.py
```

### Output:
```text
==================================================
 LOCAL BLOCKCHAIN CONTRACT DEPLOYMENT
==================================================

Network: Ganache Local
RPC: http://127.0.0.1:7545
Deployer Account: 0x14ef5fff19927974e58E6a6d7B15bD68499CEB8F
Wallet Balance: 1000.0000 ETH

Deploying smart contract...

✓ Contract deployed
Contract address:
0x54B1088417B94fBa7B4e604C5EcD2D0cc50513cD

Transaction hash:
4b0c9b77140e5d2f000de63e3bcaebf722e7a91107d142e07866a06fc5d205a9

Block number:
1

✓ Deployment successful
==================================================
[INFO] Updated CONTRACT_ADDRESS in .env
```
`deploy.py` automatically writes `CONTRACT_ADDRESS` into your `.env` file.

---

## Running the Pipeline

### 1. Full Discovery & Registration Pipeline
Run the complete pipeline on an input face image:

```powershell
python app.py --image input/person.jpg --threshold 0.55
```

**Options:**
* `--image, -i`: Path to input face image (required).
* `--threshold, -t`: Minimum similarity score threshold (default: `0.55`).
* `--provider, -p`: Search provider (`serpapi`, `serper`, `searchapi`, or `direct`).
* `--max-candidates, -m`: Number of candidate results to discover (default: `10`).
* `--skip-blockchain`: Skip on-chain write (dry run).

### Output:
```text
============================================================
 FACE IDENTIFICATION & BLOCKCHAIN VERIFICATION
 HH Goa 2026 Shortlisting Task 3 Pipeline
============================================================

[1] INPUT
Image: input/person.jpg

[2] FACE DETECTION
  Detecting face and extracting 128-d embedding...
  ✓ Face detected
    Confidence: 93.6%
    Bounding Box: (365, 186, 286, 399)
  ✓ Face encoding generated (128-d SFace feature vector)

[3] WEB SEARCH
  Provider: DirectWeb
  ✓ Reverse image search started
  ✓ 10 candidate results found dynamically from the web

[4] FACE MATCHING
  Fetching candidate 1/10: Child... [OK]
  Fetching candidate 2/10: 'Anxiety' - James Arnold... [OK]
  Fetching candidate 3/10: Sid Haig Portrait... [OK]
  ...
  Candidate 1: 57.9% <-- BEST MATCH
  Candidate 2: 57.1%
  Candidate 3: 56.5%

  ✓ BEST MATCH FOUND
  Similarity: 57.9%
  Source URL: https://www.flickr.com/photos/93898462@N03/48963025276
  Title:      Sensual portrait

[5] CONTENT REGISTRATION
  ✓ Image downloaded to: output\matched_image.jpg
  ✓ SHA-256 generated

  Image SHA-256 (File Fingerprint):
  cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9

[6] BLOCKCHAIN
  Blockchain:       Local Ganache
  Contract address: 0x54B1088417B94fBa7B4e604C5EcD2D0cc50513cD
  Wallet address:   0x14ef5fff19927974e58E6a6d7B15bD68499CEB8F
  Image SHA-256:    cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9
  Submitting transaction to smart contract...
  ✓ Transaction submitted
  ✓ Transaction confirmed on-chain

  Transaction hash: fb0f811dbf034c8fd847f3a8f892b10757b1ad67752d789a0e211de45fb3fcc1
  Block number:     2
  Record ID:        1
  Gas used:         184198

  Metadata saved to: output\result.json

============================================================
 REGISTRATION COMPLETE
============================================================
```

---

## Verifying Media Integrity

Verify whether the local content matches the on-chain fingerprint recorded in Ganache:

```powershell
python verify.py --image output/matched_image.jpg --record 1
```

### When File Matches:
```text
============================================================
 BLOCKCHAIN VERIFICATION
 Tamper-Evidence & Integrity Check
============================================================

Target File: output/matched_image.jpg
Record ID:   1

Calculating SHA-256 hash of current local file...

Network: Local Ganache
Record ID: 1
Connecting to Local Ganache smart contract...
Contract Address:  0x54B1088417B94fBa7B4e604C5EcD2D0cc50513cD
Record Timestamp:  2026-09-04 17:53:21 UTC
Source URL:        https://www.flickr.com/photos/93898462@N03/48963025276
Submitter Account: 0x14ef5fff19927974e58E6a6d7B15bD68499CEB8F

--------------------------------------------------
Blockchain hash:
cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9

Current file hash:
cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9
--------------------------------------------------

✓ HASH MATCH
✓ VERIFICATION PASSED
The current file matches the fingerprint recorded on the local Ganache blockchain.
File integrity is verified and tamper-free.
```

---

## Tampering Demonstration Procedure

To demonstrate tamper-evidence during evaluation or a screen recording:

### Step 1: Run Registration Pipeline
```powershell
python app.py --image input/person.jpg --threshold 0.55
```

### Step 2: Verify Initial File (Unaltered)
```powershell
python verify.py --image output/matched_image.jpg --record 1
```
*Expected Output:* `✓ HASH MATCH - ✓ VERIFICATION PASSED`

### Step 3: Tamper with the Local Image
Subtly modify the local file using the included utility:
```powershell
python tamper_demo.py --image output/matched_image.jpg
```

### Step 4: Verify Tampered File (Modified)
```powershell
python verify.py --image output/matched_image.jpg --record 1
```
*Expected Output:*
```text
--------------------------------------------------
Blockchain hash:
cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9

Current file hash:
29d0b4cf56dd49adfc63e13cf5eae47fc7afdbff62be39a3694fb230fb05ce18
--------------------------------------------------

✗ HASH MISMATCH
✗ VERIFICATION FAILED
✗ FILE HAS BEEN MODIFIED
The current file differs from the recorded version on the local Ganache blockchain.
```

### Step 5: Restore Original Image & Re-Verify
```powershell
python tamper_demo.py --image output/matched_image.jpg --restore
python verify.py --image output/matched_image.jpg --record 1
```
*Expected Output:* `✓ HASH MATCH - ✓ VERIFICATION PASSED`

---

## Automated Test Suite

Run the full automated test suite:

```powershell
pytest -v
```

All 11 unit tests execute in under 3 seconds using local EVM simulation.

---

## Limitations & Considerations

> [!WARNING]
> **Local Blockchain Ephemeral State:**
> The Ganache blockchain runs entirely on the developer's local machine. It is not publicly accessible over the internet.
> If Ganache is closed or restarted without database persistence, its mined blocks, accounts, and deployed smart contract state are reset. In that case, re-run `python blockchain/deploy.py` to redeploy the contract.

1. **Reverse-Image Search Constraints**: Commercial search engines (SerpApi/Serper) impose rate limits. Open web search providers depend on publicly indexed media.
2. **Access Restrictions & Anti-Bot Protections**: Certain social platforms (such as private Facebook groups or Instagram) require authentication and block automated HTTP downloading.
3. **Face Recognition Probabilistic Nature**:
   - Deep learning face models compute similarity percentages, not mathematical proofs of identity.
   - Significant pose variations, occlusions, or lighting changes can affect similarity scores.
4. **Blockchain Integrity Scope**:
   - The blockchain guarantees **data integrity and tamper-evidence** (proving that the verified file matches byte-for-byte what was downloaded at registration time).
   - The blockchain **does not prove that the discovered content was truthful or authentic before it was downloaded**.
   - A cryptographic hash verifies **file integrity**, not human identity.
