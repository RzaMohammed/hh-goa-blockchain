"""
Deployment script for FaceVerification Solidity smart contract to a Local Ethereum Blockchain (Ganache).
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
    print("=" * 50)
    print(" LOCAL BLOCKCHAIN CONTRACT DEPLOYMENT")
    print("=" * 50)

    rpc_url = os.getenv("LOCAL_RPC_URL", "http://127.0.0.1:7545")
    private_key = os.getenv("LOCAL_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")

    if not private_key or "your_ganache_private_key" in private_key or "your_private_key" in private_key:
        print("\n[ERROR] LOCAL_PRIVATE_KEY is not set in your .env file.")
        print("Please copy an account private key from Ganache and set LOCAL_PRIVATE_KEY in .env.")
        sys.exit(1)

    pk = private_key.strip()
    if not pk.startswith("0x"):
        pk = "0x" + pk

    try:
        account = Account.from_key(pk)
    except Exception as e:
        print(f"\n[ERROR] Invalid private key format: {e}")
        sys.exit(1)

    print(f"\nNetwork: Ganache Local")
    print(f"RPC: {rpc_url}")
    print(f"Deployer Account: {account.address}")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"\n[ERROR] Failed to connect to local blockchain at {rpc_url}")
        print("Please ensure Ganache is running (e.g. open Ganache UI or run 'npx ganache --port 7545').")
        sys.exit(1)

    balance_wei = w3.eth.get_balance(account.address)
    balance_eth = float(w3.from_wei(balance_wei, "ether"))
    print(f"Wallet Balance: {balance_eth:.4f} ETH")

    if balance_eth <= 0:
        print("\n[ERROR] Deployer account balance is 0 ETH.")
        print("Please select an account in Ganache that has development ETH.")
        sys.exit(1)

    print("\nDeploying smart contract...")
    contract_data = ensure_compiled()
    abi = contract_data["abi"]
    bytecode = contract_data["bytecode"]

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(account.address, "pending")
    latest_block = w3.eth.get_block("latest")
    
    tx_params = {
        "from": account.address,
        "nonce": nonce,
        "gas": 800000,
        "chainId": w3.eth.chain_id
    }

    if "baseFeePerGas" in latest_block and latest_block["baseFeePerGas"] is not None:
        base_fee = latest_block["baseFeePerGas"]
        max_priority_fee = w3.to_wei(1, "gwei")
        tx_params["maxFeePerGas"] = base_fee * 2 + max_priority_fee
        tx_params["maxPriorityFeePerGas"] = max_priority_fee
    else:
        tx_params["gasPrice"] = w3.eth.gas_price

    construct_txn = contract.constructor().build_transaction(tx_params)
    signed = w3.eth.account.sign_transaction(construct_txn, private_key=account.key)

    try:
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    except Exception as e:
        print(f"\n[ERROR] Failed to send transaction: {e}")
        sys.exit(1)

    tx_hex = tx_hash.hex()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    if receipt.get("status") != 1:
        print("\n[ERROR] Deployment failed or transaction reverted on-chain.")
        sys.exit(1)

    contract_address = receipt.contractAddress

    print("\n✓ Contract deployed")
    print("Contract address:")
    print(f"{contract_address}")
    print("\nTransaction hash:")
    print(f"{tx_hex}")
    print("\nBlock number:")
    print(f"{receipt['blockNumber']}")
    print("\n✓ Deployment successful")
    print("=" * 50)

    # Automatically update .env
    if os.path.exists(ENV_PATH):
        try:
            set_key(ENV_PATH, "CONTRACT_ADDRESS", contract_address)
            print(f"[INFO] Updated CONTRACT_ADDRESS in {ENV_PATH}")
        except Exception:
            print(f"[INFO] Please set CONTRACT_ADDRESS={contract_address} in .env")
    else:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"CONTRACT_ADDRESS={contract_address}\n")
        print(f"[INFO] Created .env with CONTRACT_ADDRESS={contract_address}")

    return contract_address


if __name__ == "__main__":
    deploy_contract()
