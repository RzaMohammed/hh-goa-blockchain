"""
Tests for blockchain client and smart contract logic.
Uses Py-EVM local tester provider for fast, deterministic contract verification.
"""
import json
import pytest
from web3 import Web3, EthereumTesterProvider
from utils.hashing import hash_bytes, hex_to_bytes32, bytes32_to_hex


@pytest.fixture
def local_evm():
    """Sets up an in-memory EVM testnet with deployed FaceVerification contract."""
    w3 = Web3(EthereumTesterProvider())
    with open("blockchain/contract_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    contract = w3.eth.contract(abi=data["abi"], bytecode=data["bytecode"])
    tx_hash = contract.constructor().transact({"from": w3.eth.accounts[0]})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_instance = w3.eth.contract(address=receipt.contractAddress, abi=data["abi"])
    return {
        "w3": w3,
        "contract": contract_instance,
        "deployer": w3.eth.accounts[0],
        "user": w3.eth.accounts[1]
    }


def test_contract_initial_state(local_evm):
    contract = local_evm["contract"]
    count = contract.functions.recordCount().call()
    assert count == 0


def test_register_and_retrieve_record(local_evm):
    contract = local_evm["contract"]
    w3 = local_evm["w3"]
    user = local_evm["user"]

    sample_content = b"Candidate face image content bytes"
    expected_hex = hash_bytes(sample_content)
    bytes32_data = hex_to_bytes32(expected_hex)
    source_url = "https://instagram.com/p/sample_post_123"

    # Register record
    tx = contract.functions.registerRecord(bytes32_data, source_url).transact({"from": user})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    assert receipt["status"] == 1

    # Check record count
    count = contract.functions.recordCount().call()
    assert count == 1

    # Retrieve record
    data_hash, ret_url, timestamp, submitter = contract.functions.getRecord(1).call()
    assert bytes32_to_hex(data_hash) == expected_hex
    assert ret_url == source_url
    assert submitter == user
    assert timestamp > 0


def test_invalid_record_reverts(local_evm):
    contract = local_evm["contract"]
    with pytest.raises(Exception):
        contract.functions.getRecord(999).call()
