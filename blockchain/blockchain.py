"""
Web3.py Ethereum Sepolia client for interacting with the FaceVerification smart contract.
Handles signing transactions, recording SHA-256 fingerprints, and querying on-chain records.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, Tuple
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

from utils.hashing import hex_to_bytes32, bytes32_to_hex

load_dotenv()
logger = logging.getLogger(__name__)

SEPOLIA_CHAIN_ID = 11155111
CONTRACT_DATA_PATH = os.path.join(os.path.dirname(__file__), "contract_data.json")


class BlockchainError(Exception):
    """Base exception for blockchain-related errors."""
    pass


class InsufficientFundsError(BlockchainError):
    """Raised when the wallet has insufficient funds for transaction gas."""
    pass


class RecordNotFoundError(BlockchainError):
    """Raised when a requested verification record does not exist."""
    pass


class BlockchainClient:
    """
    Manages Web3 connection to Ethereum Sepolia and contract interactions.
    """
    def __init__(
        self,
        rpc_url: Optional[str] = None,
        private_key: Optional[str] = None,
        contract_address: Optional[str] = None,
        use_local_evm: bool = False
    ):
        self.use_local_evm = use_local_evm
        self.rpc_url = rpc_url or os.getenv("RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")
        self.private_key = private_key or os.getenv("PRIVATE_KEY")
        self.contract_address = contract_address or os.getenv("CONTRACT_ADDRESS")

        # Load contract ABI
        if not os.path.exists(CONTRACT_DATA_PATH):
            raise BlockchainError(f"Contract artifact not found at {CONTRACT_DATA_PATH}. Run deploy.py first.")

        with open(CONTRACT_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.abi = data["abi"]
            self.bytecode = data.get("bytecode", "")

        if self.use_local_evm:
            from web3 import EthereumTesterProvider
            self.w3 = Web3(EthereumTesterProvider())
            self.account = Account.from_key(self.w3.eth.account.create().key)
            # Fund account in tester
            tester_account = self.w3.eth.accounts[0]
            self.w3.eth.send_transaction({
                "from": tester_account,
                "to": self.account.address,
                "value": self.w3.to_wei(10, "ether")
            })
            # Deploy contract on local EVM
            factory = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
            tx = factory.constructor().transact({"from": tester_account})
            rec = self.w3.eth.wait_for_transaction_receipt(tx)
            self.contract_address = rec.contractAddress
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
            logger.info(f"Local EVM initialized. Contract deployed at {self.contract_address}")
            return

        # Connect to Web3 provider (Ethereum Sepolia)
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise BlockchainError(
                f"Failed to connect to Ethereum node at {self.rpc_url}. "
                "Please verify your internet connection or check RPC_URL in .env."
            )

        # Set up account if private key is provided
        self.account = None
        if self.private_key:
            try:
                pk = self.private_key.strip()
                if not pk.startswith("0x"):
                    pk = "0x" + pk
                self.account = Account.from_key(pk)
            except Exception as e:
                raise BlockchainError(f"Invalid private key format: {e}")

        # Set up contract instance if address provided
        self.contract = None
        if self.contract_address:
            try:
                checksum_address = self.w3.to_checksum_address(self.contract_address)
                self.contract = self.w3.eth.contract(address=checksum_address, abi=self.abi)
            except Exception as e:
                raise BlockchainError(f"Invalid contract address '{self.contract_address}': {e}")

    def get_network_info(self) -> Dict[str, Any]:
        """Returns details about the connected Ethereum network."""
        chain_id = self.w3.eth.chain_id
        is_sepolia = (chain_id == SEPOLIA_CHAIN_ID)
        network_name = "Ethereum Sepolia" if is_sepolia else f"Unknown Network (Chain ID: {chain_id})"
        latest_block = self.w3.eth.block_number
        return {
            "chain_id": chain_id,
            "network_name": network_name,
            "is_sepolia": is_sepolia,
            "latest_block": latest_block,
            "rpc_url": self.rpc_url
        }

    def get_wallet_balance(self) -> float:
        """Returns wallet balance in ETH."""
        if not self.account:
            raise BlockchainError("No wallet configured (PRIVATE_KEY missing).")
        balance_wei = self.w3.eth.get_balance(self.account.address)
        return float(self.w3.from_wei(balance_wei, "ether"))

    def register_hash(self, data_hash_hex: str, source_url: str) -> Dict[str, Any]:
        """
        Submits a transaction to the smart contract to store the SHA-256 fingerprint.
        Waits for confirmation on the blockchain and returns receipt data.
        """
        if not self.contract:
            raise BlockchainError("Smart contract address is not configured. Set CONTRACT_ADDRESS in .env.")
        if not self.account:
            raise BlockchainError("Wallet private key is not configured. Set PRIVATE_KEY in .env.")

        balance_eth = self.get_wallet_balance()
        if balance_eth <= 0:
            raise InsufficientFundsError(
                f"Wallet {self.account.address} has {balance_eth} ETH. "
                "You need Sepolia testnet ETH to pay for transaction gas. "
                "Get free test ETH at: https://cloud.google.com/application/web3/faucet/ethereum/sepolia "
                "or https://faucets.chain.link/"
            )

        bytes32_hash = hex_to_bytes32(data_hash_hex)
        account_address = self.account.address

        # Build transaction
        nonce = self.w3.eth.get_transaction_count(account_address, "pending")
        latest_block = self.w3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas", self.w3.to_wei(2, "gwei"))
        max_priority_fee = self.w3.to_wei(2, "gwei")
        max_fee = base_fee * 2 + max_priority_fee

        tx_function = self.contract.functions.registerRecord(bytes32_hash, source_url)

        try:
            estimated_gas = tx_function.estimate_gas({"from": account_address})
            gas_limit = int(estimated_gas * 1.3)
        except Exception:
            gas_limit = 150000

        tx_dict = tx_function.build_transaction({
            "from": account_address,
            "nonce": nonce,
            "gas": gas_limit,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": max_priority_fee,
            "chainId": self.w3.eth.chain_id
        })

        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx_dict, private_key=self.account.key)

        # Submit transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        logger.info(f"Transaction submitted: {tx_hash_hex}. Waiting for confirmation...")

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        if receipt.get("status") != 1:
            raise BlockchainError(f"Transaction {tx_hash_hex} failed or reverted on-chain.")

        # Parse DataRegistered event to get record ID
        record_id = None
        logs = self.contract.events.DataRegistered().process_receipt(receipt)
        if logs:
            record_id = logs[0]["args"]["recordId"]
        else:
            record_id = self.contract.functions.recordCount().call()

        result_data = {
            "record_id": record_id,
            "transaction_hash": tx_hash_hex,
            "block_number": receipt["blockNumber"],
            "gas_used": receipt["gasUsed"],
            "contract_address": self.contract_address,
            "submitter": account_address,
            "data_hash": data_hash_hex,
            "source_url": source_url,
            "network": "In-Memory Local EVM" if self.use_local_evm else "Ethereum Sepolia",
            "timestamp": latest_block.get("timestamp", int(receipt.get("blockNumber", 1)))
        }

        # If running in local EVM mode, persist record to disk for subsequent local verification
        if self.use_local_evm:
            records_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "local_blockchain_records.json")
            os.makedirs(os.path.dirname(records_file), exist_ok=True)
            saved_records = {}
            if os.path.exists(records_file):
                try:
                    with open(records_file, "r", encoding="utf-8") as f:
                        saved_records = json.load(f)
                except Exception:
                    saved_records = {}
            saved_records[str(record_id)] = result_data
            with open(records_file, "w", encoding="utf-8") as f:
                json.dump(saved_records, f, indent=2)

        return result_data

    def get_record(self, record_id: int) -> Dict[str, Any]:
        """
        Retrieves a verification record from the smart contract by its record ID.
        """
        if self.use_local_evm:
            records_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "local_blockchain_records.json")
            if os.path.exists(records_file):
                try:
                    with open(records_file, "r", encoding="utf-8") as f:
                        saved = json.load(f)
                        if str(record_id) in saved:
                            rec = saved[str(record_id)]
                            return {
                                "record_id": record_id,
                                "data_hash": rec["data_hash"],
                                "source_url": rec["source_url"],
                                "timestamp": rec.get("timestamp", 0),
                                "submitter": rec["submitter"]
                            }
                except Exception:
                    pass

        if not self.contract:
            raise BlockchainError("Smart contract address is not configured. Set CONTRACT_ADDRESS in .env.")

        count = self.contract.functions.recordCount().call()
        if record_id <= 0 or record_id > count:
            raise RecordNotFoundError(
                f"Record #{record_id} does not exist. Current total records on contract: {count}."
            )

        try:
            result = self.contract.functions.getRecord(record_id).call()
            data_hash_bytes = result[0]
            source_url = result[1]
            timestamp = result[2]
            submitter = result[3]

            data_hash_hex = bytes32_to_hex(data_hash_bytes)

            return {
                "record_id": record_id,
                "data_hash": data_hash_hex,
                "source_url": source_url,
                "timestamp": timestamp,
                "submitter": submitter
            }
        except Exception as e:
            raise BlockchainError(f"Failed to query record #{record_id}: {e}")
