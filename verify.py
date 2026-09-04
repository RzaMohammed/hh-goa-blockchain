"""
Verification CLI tool for Face Identification & Blockchain Verification.
Re-hashes the local image file, queries the on-chain fingerprint from the
Ethereum Sepolia smart contract, and evaluates tamper evidence.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

from utils.hashing import hash_file, verify_hashes
from blockchain.blockchain import BlockchainClient, BlockchainError, RecordNotFoundError

load_dotenv()

# Ensure Windows PowerShell handles UTF-8 checkmarks and symbols cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify local image integrity against Ethereum Sepolia on-chain fingerprint."
    )
    parser.add_argument(
        "--image",
        "-i",
        type=str,
        default="output/matched_image.jpg",
        help="Path to the local image file to verify (default: output/matched_image.jpg)"
    )
    parser.add_argument(
        "--record",
        "-r",
        type=int,
        default=None,
        help="Blockchain record ID to verify against (default: read from output/result.json)"
    )
    parser.add_argument(
        "--contract",
        "-c",
        type=str,
        default=None,
        help="Override contract address (default: CONTRACT_ADDRESS from .env)"
    )
    parser.add_argument(
        "--rpc",
        type=str,
        default=None,
        help="Override Ethereum RPC URL (default: RPC_URL from .env)"
    )
    parser.add_argument(
        "--local-evm",
        action="store_true",
        help="Verify using local EVM record store (ideal for offline demonstration & tests)"
    )
    return parser.parse_args()


def print_banner():
    print("=" * 60)
    print(" BLOCKCHAIN VERIFICATION")
    print(" Tamper-Evidence & Integrity Check")
    print("=" * 60)


def verify():
    args = parse_args()
    print_banner()

    # 1. Locate file and determine record ID
    image_path = os.path.abspath(args.image)
    if not os.path.exists(image_path):
        print(f"\n[ERROR] File to verify not found: {args.image}")
        sys.exit(1)

    record_id = args.record
    is_local_evm = args.local_evm
    
    # Check result.json in output directory if available
    result_json_path = os.path.join(os.path.dirname(image_path), "result.json")
    if os.path.exists(result_json_path):
        try:
            with open(result_json_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                if record_id is None:
                    record_id = meta.get("blockchain", {}).get("record_id")
                net_name = meta.get("blockchain", {}).get("network", "")
                if "Local EVM" in net_name:
                    is_local_evm = True
        except Exception:
            pass

    if record_id is None:
        print("\n[ERROR] No record ID specified.")
        print("Please provide --record <ID> (e.g. python verify.py --image output/matched_image.jpg --record 1)")
        sys.exit(1)

    print(f"\nTarget File: {args.image}")
    print(f"Record ID:   {record_id}")

    # 2. Calculate current file SHA-256 hash
    print("\nCalculating SHA-256 hash of current local file...")
    try:
        current_file_hash = hash_file(image_path)
    except Exception as e:
        print(f"\n[ERROR] Failed to hash file: {e}")
        sys.exit(1)

    # 3. Connect to blockchain and query smart contract
    network_label = "In-Memory Local EVM" if is_local_evm else "Local Ganache"
    print(f"\nNetwork: {network_label}")
    print(f"Record ID: {record_id}")
    print(f"Connecting to {network_label} smart contract...")
    try:
        client = BlockchainClient(
            rpc_url=args.rpc,
            contract_address=args.contract,
            use_local_evm=is_local_evm
        )
        record = client.get_record(record_id)
    except RecordNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except BlockchainError as e:
        print(f"\n[ERROR] Blockchain error: {e}")
        if not is_local_evm and "CONTRACT_ADDRESS" in str(e):
            print("\nHint: To deploy the smart contract on your local Ganache blockchain, run:")
            print("  python blockchain/deploy.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error connecting to blockchain: {e}")
        sys.exit(1)

    blockchain_hash = record["data_hash"]
    ts_dt = datetime.utcfromtimestamp(record["timestamp"]).strftime('%Y-%m-%d %H:%M:%S UTC') if record["timestamp"] else "N/A"

    print(f"Contract Address:  {client.contract_address}")
    print(f"Record Timestamp:  {ts_dt}")
    print(f"Source URL:        {record['source_url']}")
    print(f"Submitter Account: {record['submitter']}")

    # 4. Compare hashes
    print("\n" + "-" * 50)
    print(f"Blockchain hash:\n{blockchain_hash}\n")
    print(f"Current file hash:\n{current_file_hash}")
    print("-" * 50)

    is_match = verify_hashes(blockchain_hash, current_file_hash)

    if is_match:
        print("\n✓ HASH MATCH")
        print("✓ VERIFICATION PASSED")
        print("The current file matches the fingerprint recorded on the local Ganache blockchain.")
        print("File integrity is verified and tamper-free.")
        sys.exit(0)
    else:
        print("\n✗ HASH MISMATCH")
        print("✗ VERIFICATION FAILED")
        print("✗ FILE HAS BEEN MODIFIED")
        print("The current file differs from the recorded version on the local Ganache blockchain.")
        sys.exit(2)


if __name__ == "__main__":
    verify()
