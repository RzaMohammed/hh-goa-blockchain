"""
Main CLI Pipeline for Face Identification & Blockchain Verification.
Performs face detection, web reverse-image searching, similarity ranking,
content downloading, SHA-256 fingerprinting, and on-chain registration on Ethereum Sepolia.
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

from face.detector import FaceDetector, FaceError, NoFaceDetectedError, InvalidImageError
from face.matcher import FaceMatcher
from search.reverse_search import get_search_provider, SearchError, CandidateResult
from utils.downloader import ImageDownloader, DownloadError
from utils.hashing import hash_bytes, hash_file
from blockchain.blockchain import (
    BlockchainClient,
    BlockchainError,
    InsufficientFundsError,
    RecordNotFoundError
)

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
        description="Face Identification & Blockchain Verification Pipeline - HH Goa 2026 Shortlisting Task 3"
    )
    parser.add_argument(
        "--image",
        "-i",
        type=str,
        required=True,
        help="Path to input face image (e.g., input/person.jpg)"
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=float(os.getenv("SIMILARITY_THRESHOLD", "0.60")),
        help="Minimum similarity threshold (0.0 to 1.0 or 0 to 100, default: 0.60)"
    )
    parser.add_argument(
        "--provider",
        "-p",
        type=str,
        default=os.getenv("DEFAULT_SEARCH_PROVIDER"),
        choices=["serpapi", "serper", "searchapi", "direct"],
        help="Reverse image search provider (serpapi, serper, searchapi, or direct)"
    )
    parser.add_argument(
        "--max-candidates",
        "-m",
        type=int,
        default=10,
        help="Maximum candidate results to discover and evaluate (default: 10)"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=os.getenv("OUTPUT_DIR", "output"),
        help="Directory to save downloaded matched image and metadata (default: output)"
    )
    parser.add_argument(
        "--skip-blockchain",
        action="store_true",
        help="Skip on-chain blockchain registration (useful for dry runs and offline testing)"
    )
    parser.add_argument(
        "--platform",
        choices=["all", "instagram", "github", "linkedin"],
        default="all",
        help="Target social platform to search (choices: all, instagram, github, linkedin; default: all)"
    )
    return parser.parse_args()


def print_banner():
    print("=" * 60)
    print(" FACE IDENTIFICATION & BLOCKCHAIN VERIFICATION")
    print(" HH Goa 2026 Shortlisting Task 3 Pipeline")
    print("=" * 60)


def run_pipeline():
    args = parse_args()
    print_banner()

    # -------------------------------------------------------------
    # [1] INPUT VALIDATION
    # -------------------------------------------------------------
    print("\n[1] INPUT")
    image_path = os.path.abspath(args.image)
    print(f"Image: {args.image}")

    if not os.path.exists(image_path):
        print(f"\n[ERROR] Input image file not found: {args.image}")
        sys.exit(1)

    # -------------------------------------------------------------
    # [2] FACE DETECTION & ENCODING
    # -------------------------------------------------------------
    print("\n[2] FACE DETECTION")
    try:
        detector = FaceDetector()
        matcher = FaceMatcher(detector=detector)
        print("  Detecting face and extracting 128-d embedding...")
        query_embedding, face_res, total_faces = matcher.compute_embedding_for_image(image_path)
        print("  ✓ Face detected")
        if total_faces > 1:
            print(f"    (Note: {total_faces} faces found in input; selected primary face by area)")
        print(f"    Confidence: {face_res.confidence * 100:.1f}%")
        print(f"    Bounding Box: {face_res.bbox}")
        print("  ✓ Face encoding generated (128-d SFace feature vector)")
    except NoFaceDetectedError:
        print("\n[ERROR] No face detected in the input image.")
        print("Please provide an image with a clearly visible human face.")
        sys.exit(1)
    except InvalidImageError as e:
        print(f"\n[ERROR] Failed to load image: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during face processing: {e}")
        sys.exit(1)

    # -------------------------------------------------------------
    # [3] WEB / SOCIAL MEDIA SEARCH
    # -------------------------------------------------------------
    print("\n[3] WEB SEARCH")
    try:
        provider = get_search_provider(args.provider)
        provider_name = provider.__class__.__name__.replace("SearchProvider", "")
        print(f"  Provider: {provider_name}")
        print(f"  Social Platform Target: {args.platform.upper()}")
        print("  ✓ Reverse image search started")
        candidates = provider.search(image_path, max_results=args.max_candidates, platform=args.platform)
        print(f"  ✓ {len(candidates)} candidate results found dynamically across {args.platform.upper()}")
    except SearchError as e:
        print(f"\n[ERROR] Search operation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during web search: {e}")
        sys.exit(1)

    if not candidates:
        print("\n[INFO] No candidate results returned by search provider.")
        print("Try adjusting the input image or using a different search provider.")
        sys.exit(0)

    # -------------------------------------------------------------
    # [4] CANDIDATE DOWNLOADING & FACE SIMILARITY COMPARISON
    # -------------------------------------------------------------
    print("\n[4] FACE MATCHING")
    downloader = ImageDownloader()
    evaluated_candidates = []

    for idx, cand in enumerate(candidates, start=1):
        print(f"  Fetching candidate {idx}/{len(candidates)}: {cand.title[:45]}...", end="", flush=True)
        img_bytes = None
        # Try direct image_url first, fallback to thumbnail_url
        for target_url in [cand.image_url, cand.thumbnail_url]:
            if not target_url:
                continue
            try:
                img_bytes = downloader.download_image_bytes(target_url)
                break
            except Exception:
                continue

        if not img_bytes:
            print(" [Download Failed]")
            continue

        evaluated_candidates.append({
            "title": cand.title,
            "source_url": cand.source_url,
            "image_url": cand.image_url,
            "image_bytes": img_bytes,
            "image_data": img_bytes
        })
        print(" [OK]")

    if not evaluated_candidates:
        print("\n[ERROR] Unable to download accessible image data for any discovered candidate.")
        sys.exit(1)

    # Rank candidates using face matcher
    ranked = matcher.rank_candidates(query_embedding, evaluated_candidates, threshold=args.threshold)

    print("\n  Similarity Scores:")
    best_candidate = None
    best_similarity = -1.0

    threshold_pct = args.threshold * 100.0 if args.threshold <= 1.0 else args.threshold

    for idx, item in enumerate(ranked, start=1):
        pct = item.get("similarity_percentage", 0.0)
        marker = ""
        if idx == 1 and pct >= threshold_pct:
            marker = " <-- BEST MATCH"
            best_candidate = item
            best_similarity = pct
        elif idx == 1:
            best_candidate = item
            best_similarity = pct

        print(f"  Candidate {idx}: {pct:.1f}%{marker}")

    if not best_candidate or best_similarity < threshold_pct:
        print(f"\n[INFO] Highest similarity ({best_similarity:.1f}%) is below configured threshold ({threshold_pct:.1f}%).")
        print("No match met the similarity criteria.")
        print("Note: The system describes candidates by face similarity and does not claim absolute identity.")
        sys.exit(0)

    print("\n  ✓ BEST MATCH FOUND")
    print(f"  Similarity: {best_similarity:.1f}%")
    print(f"  Source URL: {best_candidate['source_url']}")
    print(f"  Title:      {best_candidate['title']}")

    # -------------------------------------------------------------
    # [5] CONTENT REGISTRATION & SHA-256 HASHING
    # -------------------------------------------------------------
    print("\n[5] CONTENT REGISTRATION")
    os.makedirs(args.output_dir, exist_ok=True)
    matched_image_path = os.path.join(args.output_dir, "matched_image.jpg")
    downloader.save_image(best_candidate["image_bytes"], matched_image_path)
    print(f"  ✓ Image downloaded to: {matched_image_path}")

    # Compute SHA-256 cryptographic fingerprint from raw file bytes
    file_sha256 = hash_file(matched_image_path)
    print("  ✓ SHA-256 generated")
    print(f"\n  Image SHA-256 (File Fingerprint):\n  {file_sha256}")

    # -------------------------------------------------------------
    # [6] BLOCKCHAIN SMART CONTRACT REGISTRATION
    # -------------------------------------------------------------
    print("\n[6] BLOCKCHAIN")
    blockchain_info = {
        "status": "Skipped" if args.skip_blockchain else "Pending",
        "network": "Local Ganache",
        "contract_address": os.getenv("CONTRACT_ADDRESS", "Not Configured"),
        "transaction_hash": None,
        "record_id": None
    }

    if args.skip_blockchain:
        print("  [INFO] Blockchain registration skipped via --skip-blockchain flag.")
    else:
        try:
            client = BlockchainClient(use_local_evm=args.local_evm)
            net_info = client.get_network_info() if not args.local_evm else {"network_name": "In-Memory Local EVM (Testnet)"}
            print(f"  Blockchain:       {net_info['network_name']}")
            print(f"  Contract address: {client.contract_address}")
            print(f"  Wallet address:   {client.account.address if client.account else 'None'}")
            print(f"  Image SHA-256:    {file_sha256}")
            print("  Submitting transaction to smart contract...")

            tx_result = client.register_hash(
                data_hash_hex=file_sha256,
                source_url=best_candidate["source_url"]
            )

            print("  ✓ Transaction submitted")
            print("  ✓ Transaction confirmed on-chain")
            print(f"\n  Transaction hash: {tx_result['transaction_hash']}")
            print(f"  Block number:     {tx_result['block_number']}")
            print(f"  Record ID:        {tx_result['record_id']}")
            print(f"  Gas used:         {tx_result['gas_used']}")

            blockchain_info.update({
                "status": "Confirmed",
                "transaction_hash": tx_result["transaction_hash"],
                "record_id": tx_result["record_id"],
                "block_number": tx_result["block_number"],
                "gas_used": tx_result["gas_used"],
                "submitter": tx_result["submitter"]
            })

        except InsufficientFundsError as e:
            print("\n  " + "!" * 55)
            print(f"  [ERROR] {e}")
            print("  " + "!" * 55)
            print("  Fingerprint generated and image saved, but on-chain registration aborted.")
        except BlockchainError as e:
            print(f"\n  [ERROR] Blockchain error: {e}")
            print("  Fingerprint generated and image saved, but on-chain registration aborted.")
        except Exception as e:
            print(f"\n  [ERROR] Unexpected error connecting to blockchain: {e}")

    # -------------------------------------------------------------
    # [7] PERSIST METADATA
    # -------------------------------------------------------------
    metadata = {
        "source_url": best_candidate["source_url"],
        "title": best_candidate["title"],
        "similarity_score_pct": best_similarity,
        "similarity_description": "Face similarity match (not absolute identity)",
        "timestamp_iso": datetime.utcnow().isoformat() + "Z",
        "timestamp_unix": int(time.time()),
        "local_filename": matched_image_path,
        "sha256_hash": file_sha256,
        "blockchain": blockchain_info
    }

    result_json_path = os.path.join(args.output_dir, "result.json")
    downloader.save_metadata(metadata, result_json_path)
    print(f"\n  Metadata saved to: {result_json_path}")

    print("\n" + "=" * 60)
    print(" REGISTRATION COMPLETE")
    print("=" * 60)
    print("Next step: Run verification to check file integrity:")
    record_id_str = str(blockchain_info.get("record_id") or 1)
    print(f"  python verify.py --image {matched_image_path} --record {record_id_str}\n")


if __name__ == "__main__":
    run_pipeline()
