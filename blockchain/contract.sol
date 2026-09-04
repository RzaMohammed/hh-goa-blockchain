// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title FaceVerification
 * @dev Stores and verifies cryptographic fingerprints (SHA-256) of face image content.
 * Intended for the HH Goa 2026 Shortlisting Task 3: Face Identification & Blockchain Verification.
 */
contract FaceVerification {
    struct VerificationRecord {
        bytes32 dataHash;      // SHA-256 cryptographic fingerprint of the file
        string sourceUrl;      // Source web or social media URL where content was discovered
        uint256 timestamp;     // Block timestamp when registered on-chain
        address submitter;     // Address of the wallet that registered the record
    }

    // Incremental counter for verification records
    uint256 public recordCount;

    // Mapping from recordId (1-indexed) to VerificationRecord
    mapping(uint256 => VerificationRecord) public records;

    // Event emitted upon successful hash registration
    event DataRegistered(
        uint256 indexed recordId,
        bytes32 dataHash,
        string sourceUrl,
        uint256 timestamp,
        address indexed submitter
    );

    /**
     * @notice Registers a new cryptographic fingerprint and source URL on the blockchain.
     * @param _dataHash 32-byte SHA-256 hash of the downloaded image file.
     * @param _sourceUrl Discovered source URL where the matching content originated.
     * @return recordId Unique incremental ID assigned to this record.
     */
    function registerRecord(bytes32 _dataHash, string memory _sourceUrl) external returns (uint256) {
        require(_dataHash != bytes32(0), "Data hash cannot be empty");
        
        recordCount++;
        records[recordCount] = VerificationRecord({
            dataHash: _dataHash,
            sourceUrl: _sourceUrl,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        emit DataRegistered(recordCount, _dataHash, _sourceUrl, block.timestamp, msg.sender);
        return recordCount;
    }

    /**
     * @notice Retrieves a verification record by its record ID.
     * @param _recordId The ID of the record to query (1 to recordCount).
     * @return dataHash 32-byte SHA-256 hash stored on-chain.
     * @return sourceUrl Discovered source URL.
     * @return timestamp Block timestamp when registered.
     * @return submitter Wallet address that submitted the transaction.
     */
    function getRecord(uint256 _recordId) external view returns (
        bytes32 dataHash,
        string memory sourceUrl,
        uint256 timestamp,
        address submitter
    ) {
        require(_recordId > 0 && _recordId <= recordCount, "Record does not exist");
        VerificationRecord memory rec = records[_recordId];
        return (rec.dataHash, rec.sourceUrl, rec.timestamp, rec.submitter);
    }
}
