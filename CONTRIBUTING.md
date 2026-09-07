# Contributing to Biometric Blockchain Verification

Thank you for contributing to the **Face Identification & Blockchain Verification Engine**! We welcome improvements to biometric facial algorithms, smart contract interfaces, reverse image search engines, and the React frontend.

---

## Development Setup

### 1. Prerequisites
- **Python 3.10+** (with `pip`)
- **Node.js 18+** (with `npm`)
- **Ganache** (GUI or CLI at port 7545 / 8545)

### 2. Python Environment
```bash
# Clone the repository
git clone https://github.com/vvgaditya-8123/hh-goa-blockchain.git
cd hh-goa-blockchain

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Smart Contract & Blockchain Setup
1. Launch Ganache (RPC URL: `http://127.0.0.1:7545` or `8545`).
2. Copy a development private key into `.env` as `LOCAL_PRIVATE_KEY`.
3. Deploy the smart contract:
```bash
python blockchain/deploy.py
```
4. Update `CONTRACT_ADDRESS` in `.env` with the printed address.

---

## Git Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description |
|---|---|
| `feat` | New feature or functional enhancement |
| `fix` | Bug fix or error resolution |
| `docs` | Documentation updates (README, docstrings, specs) |
| `test` | Adding or updating unit/integration tests |
| `chore` | Tooling, config files, build tasks, dependencies |
| `refactor` | Code restructuring without behavioral changes |

### Example Commit Messages:
- `feat(blockchain): support configurable gas limit in contract calls`
- `fix(face): handle edge case when no landmarks are detected`
- `docs(api): document websocket events for pipeline progress`

---

## Pull Request Checklist

Before submitting a pull request, ensure:
- [ ] Code follows formatting standards (Ruff / Python PEP 8).
- [ ] Python code compiles cleanly: `python -m py_compile utils/hashing.py tests/test_hashing.py app.py frontend.py`.
- [ ] Unit tests pass: `python -m pytest tests/`.
- [ ] Frontend builds without errors: `npm --prefix frontend run build`.
- [ ] Commit history is clean and descriptive.
