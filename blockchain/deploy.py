"""
Deployment script for FaceVerification Solidity smart contract to Ethereum Sepolia.
Compiles the contract, signs the deployment transaction, and updates .env with the new contract address.
"""
import os
import sys
import json
import logging
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv, set_key

load_dotenv()

# Ensure Windows PowerShell handles UTF-8 checkmarks and symbols cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
CONTRACT_DATA_PATH = os.path.join(os.path.dirname(__file__), "contract_data.json")
SOL_PATH = os.path.join(os.path.dirname(__file__), "contract.sol")


def ensure_compiled():
    """Ensures contract_data.json exists or compiles from contract.sol."""
    if os.path.exists(CONTRACT_DATA_PATH):
        with open(CONTRACT_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    # Compile using solcx if json is missing
    import solcx
    if "0.8.20" not in [str(v) for v in solcx.get_installed_solc_versions()]:
        solcx.install_solc("0.8.20")

    with open(SOL_PATH, "r", encoding="utf-8") as f:
        source = f.read()

    compiled = solcx.compile_standard({
        "language": "Solidity",
        "sources": {"contract.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode"]}
            }
        }
    }, solc_version="0.8.20")

    contract_info = compiled["contracts"]["contract.sol"]["FaceVerification"]
    data = {
        "abi": contract_info["abi"],
        "bytecode": contract_info["evm"]["bytecode"]["object"]
    }
    with open(CONTRACT_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data


def deploy_contract():
    print("=" * 60)
    print("  ETHEREUM SEPOLIA - CONTRACT DEPLOYMENT")
    print("=" * 60)

    rpc_url = os.getenv("RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")
    private_key = os.getenv("PRIVATE_KEY")

    if not private_key or "your_private_key" in private_key:
        print("\n[ERROR] PRIVATE_KEY is not set in your .env file.")
        print("Please configure PRIVATE_KEY in .env before deploying.")
        sys.exit(1)

    pk = private_key.strip()
    if not pk.startswith("0x"):
        pk = "0x" + pk

    account = Account.from_key(pk)
    print(f"\n[1] Deployer Wallet: {account.address}")
    print(f"[2] Connecting to RPC: {rpc_url}")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"\n[ERROR] Failed to connect to Ethereum node at {rpc_url}")
        sys.exit(1)

    chain_id = w3.eth.chain_id
    network_name = "Ethereum Sepolia (Testnet)" if chain_id == 11155111 else f"Chain ID {chain_id}"
    print(f"[3] Network: {network_name}")

    balance_wei = w3.eth.get_balance(account.address)
    balance_eth = float(w3.from_wei(balance_wei, "ether"))
    print(f"[4] Wallet Balance: {balance_eth:.5f} ETH")

    min_deploy_eth = 0.002
    if balance_eth < min_deploy_eth:
        print("\n" + "!" * 60)
        print("[ERROR] INSUFFICIENT SEPOLIA ETH TO DEPLOY CONTRACT")
        print("!" * 60)
        print(f"Deployer address: {account.address}")
        print(f"Current balance:  {balance_eth:.6f} ETH (minimum ~{min_deploy_eth} ETH needed)")
        print("You need Sepolia testnet ETH to pay for transaction gas.")
        print("\nGet free Sepolia test ETH from these official faucets:")
        print("1. Google Cloud Web3 Faucet: https://cloud.google.com/application/web3/faucet/ethereum/sepolia")
        print("2. Chainlink Sepolia Faucet: https://faucets.chain.link/")
        print("3. Alchemy Sepolia Faucet:   https://www.alchemy.com/faucets/ethereum-sepolia")
        print("4. PoW Sepolia Faucet:       https://sepolia-faucet.pk910.de/")
        print("!" * 60)
        sys.exit(1)

    print("\n[5] Compiling and loading contract artifacts...")
    contract_data = ensure_compiled()
    abi = contract_data["abi"]
    bytecode = contract_data["bytecode"]

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(account.address, "pending")
    latest_block = w3.eth.get_block("latest")
    base_fee = latest_block.get("baseFeePerGas", w3.to_wei(2, "gwei"))
    max_priority_fee = w3.to_wei(2, "gwei")
    max_fee = base_fee * 2 + max_priority_fee

    print("[6] Building deployment transaction...")
    construct_txn = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 800000,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": max_priority_fee,
        "chainId": chain_id
    })

    print("[7] Signing transaction with private key...")
    signed = w3.eth.account.sign_transaction(construct_txn, private_key=account.key)

    print("[8] Sending transaction to Ethereum Sepolia...")
    try:
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    except Exception as e:
        if "insufficient funds" in str(e).lower():
            print("\n" + "!" * 60)
            print("[ERROR] INSUFFICIENT SEPOLIA ETH TO PAY FOR GAS")
            print("!" * 60)
            print(f"Deployer address: {account.address}")
            print("Get free test ETH at: https://cloud.google.com/application/web3/faucet/ethereum/sepolia")
            print("!" * 60)
            sys.exit(1)
        else:
            print(f"\n[ERROR] Failed to send transaction: {e}")
            sys.exit(1)

    tx_hex = tx_hash.hex()
    print(f"    Transaction Hash: {tx_hex}")
    print("    Waiting for block confirmation on-chain...")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    if receipt.get("status") != 1:
        print("\n[ERROR] Deployment failed or transaction reverted on-chain.")
        sys.exit(1)

    contract_address = receipt.contractAddress
    print("\n" + "=" * 60)
    print("  CONTRACT DEPLOYED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Contract Address: {contract_address}")
    print(f"Transaction:      {tx_hex}")
    print(f"Block Number:     {receipt['blockNumber']}")
    print(f"Gas Used:         {receipt['gasUsed']}")
    print("=" * 60)

    # Automatically update .env
    if os.path.exists(ENV_PATH):
        try:
            set_key(ENV_PATH, "CONTRACT_ADDRESS", contract_address)
            print(f"\n[INFO] Updated CONTRACT_ADDRESS in {ENV_PATH}")
        except Exception as e:
            print(f"\n[INFO] Please add CONTRACT_ADDRESS={contract_address} to your .env file.")
    else:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"CONTRACT_ADDRESS={contract_address}\n")
        print(f"\n[INFO] Created .env with CONTRACT_ADDRESS={contract_address}")

    return contract_address


if __name__ == "__main__":
    deploy_contract()
