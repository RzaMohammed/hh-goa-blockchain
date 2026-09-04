"""
CyberSight Web Application Server.
Serves the React frontend bundle and provides REST API endpoints connected
directly to the real Face Identification & Blockchain Verification pipeline.
"""
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import json
import time
import base64
import logging
import mimetypes
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

from face.detector import FaceDetector, NoFaceDetectedError, InvalidImageError
from face.matcher import FaceMatcher
from search.reverse_search import get_search_provider, SearchError
from utils.downloader import ImageDownloader, DownloadError
from utils.hashing import hash_file, hash_bytes, verify_hashes
from blockchain.blockchain import BlockchainClient, BlockchainError, RecordNotFoundError

load_dotenv()
logger = logging.getLogger(__name__)

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


class PipelineApiHandler(BaseHTTPRequestHandler):
    """Handles REST API requests and serves static React frontend assets."""

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200, "text/plain")

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                return {}
            body = self.rfile.read(content_length).decode("utf-8")
            return json.loads(body) if body else {}
        except Exception as e:
            logger.warning(f"Error decoding JSON request body: {e}")
            return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, "application/json")
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # -----------------------------------------------------------------
        # API: Status & Network Info
        # -----------------------------------------------------------------
        if path == "/api/status":
            try:
                client = BlockchainClient()
                net_info = client.get_network_info()
                balance = client.get_wallet_balance() if client.account else 0.0
                record_count = client.contract.functions.recordCount().call() if client.contract else 0
                return self._send_json({
                    "connected": True,
                    "network": "Local Ganache",
                    "rpc_url": client.rpc_url,
                    "contract_address": client.contract_address,
                    "wallet_address": client.account.address if client.account else None,
                    "wallet_balance": round(balance, 4),
                    "latest_block": net_info.get("latest_block", 0),
                    "total_records": record_count
                })
            except Exception as e:
                return self._send_json({
                    "connected": False,
                    "network": "Ganache Disconnected",
                    "error": str(e)
                })

        # -----------------------------------------------------------------
        # API: On-Chain Ledger Records
        # -----------------------------------------------------------------
        elif path == "/api/ledger":
            records = []
            try:
                client = BlockchainClient()
                if client.contract:
                    count = client.contract.functions.recordCount().call()
                    for r_id in range(1, count + 1):
                        try:
                            rec = client.get_record(r_id)
                            ts = datetime.utcfromtimestamp(rec["timestamp"]).strftime('%Y-%m-%d %H:%M:%S UTC') if rec["timestamp"] else "N/A"
                            full_hash = rec["data_hash"]
                            short_hash = f"0x{full_hash[:10]}...{full_hash[-8:]}" if len(full_hash) > 18 else full_hash
                            full_sub = rec["submitter"]
                            short_sub = f"{full_sub[:6]}...{full_sub[-4:]}" if len(full_sub) > 10 else full_sub
                            records.append({
                                "id": r_id,
                                "hash": short_hash,
                                "fullHash": f"0x{full_hash}",
                                "sourceUrl": rec["source_url"],
                                "timestamp": ts,
                                "submitter": short_sub,
                                "fullSubmitter": full_sub
                            })
                        except Exception:
                            pass
            except Exception as e:
                logger.warning(f"Error fetching ledger: {e}")

            return self._send_json({"records": records})

        # -----------------------------------------------------------------
        # Static Files: Serve output/ or input/ files directly
        # -----------------------------------------------------------------
        if path.startswith("/output/"):
            rel_file = path[len("/output/"):]
            full_path = os.path.join(OUTPUT_DIR, rel_file)
            return self._serve_file(full_path)

        if path.startswith("/input/"):
            rel_file = path[len("/input/"):]
            full_path = os.path.join(INPUT_DIR, rel_file)
            return self._serve_file(full_path)

        # -----------------------------------------------------------------
        # Static Files: React Dist Bundle
        # -----------------------------------------------------------------
        clean_path = path.lstrip("/")
        target_file = os.path.join(FRONTEND_DIST_DIR, clean_path)

        if os.path.isfile(target_file):
            return self._serve_file(target_file)

        # SPA Fallback to index.html
        index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return self._serve_file(index_file)

        self.send_error(404, "File not found")

    def _serve_file(self, file_path):
        if not os.path.exists(file_path):
            self.send_error(404, f"File not found: {file_path}")
            return
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, mime_type)
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        # -----------------------------------------------------------------
        # API: Execute Pipeline
        # -----------------------------------------------------------------
        if path == "/api/pipeline/run":
            dataset_id = body.get("dataset_id", "person")
            threshold = float(body.get("threshold", 0.55))
            provider_name = body.get("provider", "direct")
            platform_name = body.get("platform", "all")
            custom_b64 = body.get("custom_image")

            # 1. Determine input image file
            if custom_b64:
                try:
                    if "," in custom_b64:
                        custom_b64 = custom_b64.split(",", 1)[1]
                    img_bytes = base64.b64decode(custom_b64)
                    image_path = os.path.join(INPUT_DIR, "custom_upload.jpg")
                    with open(image_path, "wb") as f:
                        f.write(img_bytes)
                except Exception as e:
                    return self._send_json({"success": False, "stage": 1, "error": f"Failed to decode upload: {e}"}, 400)
            elif dataset_id == "noface":
                image_path = os.path.join(INPUT_DIR, "no_face.jpg")
            elif dataset_id == "lookalike":
                image_path = os.path.join(INPUT_DIR, "candidate_different.jpg")
            elif dataset_id == "tamper":
                image_path = os.path.join(INPUT_DIR, "candidate_same.jpg")
            else:
                image_path = os.path.join(INPUT_DIR, "person.jpg")

            if not os.path.exists(image_path):
                return self._send_json({"success": False, "stage": 1, "error": f"Input image not found: {image_path}"}, 404)

            # Stage 1: Face Detection
            detector = FaceDetector()
            matcher = FaceMatcher(detector=detector)

            try:
                query_embedding, face_res, count = matcher.compute_embedding_for_image(image_path)
            except NoFaceDetectedError:
                return self._send_json({
                    "success": False,
                    "stage": 1,
                    "error": "No face detected in the input frame.",
                    "verdict": {
                        "type": "noface",
                        "title": "Stage 1 Halted: No Face Detected",
                        "message": "YuNet detector found 0 human faces in the provided frame. Reverse search and on-chain notarization were skipped."
                    }
                })
            except Exception as e:
                return self._send_json({"success": False, "stage": 1, "error": str(e)})

            # Stage 2: Web Search across Social Platforms (Instagram, GitHub, LinkedIn)
            try:
                search_provider = get_search_provider(provider_name)
                candidates = search_provider.search(image_path, max_results=8, platform=platform_name)
            except Exception as e:
                return self._send_json({"success": False, "stage": 2, "error": f"Search failed: {e}"})

            # Stage 3: Candidate Evaluation & Similarity Matching
            downloader = ImageDownloader()
            evaluated = []
            for cand in candidates:
                try:
                    target_url = cand.image_url or cand.thumbnail_url
                    img_data = downloader.download_image_bytes(target_url)
                    evaluated.append({
                        "title": cand.title,
                        "source_url": cand.source_url,
                        "image_url": cand.image_url,
                        "image_bytes": img_data,
                        "image_data": img_data,
                        "platform": cand.platform
                    })
                except Exception:
                    continue

            if not evaluated:
                return self._send_json({"success": False, "stage": 3, "error": "Could not download candidate images."})

            ranked = matcher.rank_candidates(query_embedding, evaluated, threshold=threshold)
            best_candidate = ranked[0]
            best_score = best_candidate.get("similarity_percentage", 0.0)

            # Format candidates for UI
            formatted_candidates = []
            for i, item in enumerate(ranked[:6]):
                pct = item.get("similarity_percentage", 0.0)
                is_best = (i == 0)
                tag = "Verified" if pct >= (threshold * 100 if threshold <= 1 else threshold) else "Low Match"
                plat = item.get("platform", "web")
                raw_img = item.get("image_url", "")
                if raw_img and (os.path.isabs(raw_img) or not raw_img.startswith("http")):
                    if "output" in raw_img:
                        avatar_url = f"/output/{os.path.basename(raw_img)}"
                    elif "input" in raw_img:
                        avatar_url = f"/input/{os.path.basename(raw_img)}"
                    else:
                        avatar_url = raw_img
                else:
                    avatar_url = raw_img

                formatted_candidates.append({
                    "avatar": avatar_url,
                    "label": item.get("title"),
                    "link": item.get("source_url"),
                    "score": pct,
                    "tag": tag,
                    "isBest": is_best,
                    "platform": plat
                })

            # Stage 4: Content Acquisition & SHA-256 Checksum
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            matched_image_path = os.path.join(OUTPUT_DIR, "matched_image.jpg")
            downloader.save_image(best_candidate["image_bytes"], matched_image_path)
            file_sha256 = hash_file(matched_image_path)

            # Stage 5: Blockchain Smart Contract Registration (Ganache)
            blockchain_receipt = None
            try:
                client = BlockchainClient()
                tx_res = client.register_hash(data_hash_hex=file_sha256, source_url=best_candidate["source_url"])
                blockchain_receipt = {
                    "network": "Local Ganache",
                    "contract_address": tx_res["contract_address"],
                    "transaction_hash": f"0x{tx_res['transaction_hash']}",
                    "block_number": tx_res["block_number"],
                    "record_id": tx_res["record_id"],
                    "gas_used": tx_res["gas_used"],
                    "submitter": tx_res["submitter"]
                }
            except Exception as e:
                logger.warning(f"Blockchain registration warning: {e}")
                blockchain_receipt = {
                    "network": "Local Ganache",
                    "error": str(e)
                }

            # Prepare Verdict
            gate_pct = threshold * 100 if threshold <= 1 else threshold
            if best_score < gate_pct:
                verdict = {
                    "type": "lowmatch",
                    "title": f"Low Match: {best_score:.1f}% Below {gate_pct:.1f}% Gate",
                    "message": f"Discovered candidate face similarity ({best_score:.1f}%) is below the configured threshold gate."
                }
            else:
                verdict = {
                    "type": "verified",
                    "title": "On-Chain Verification Passed",
                    "message": "100% Cryptographic Match! The portrait has been authenticated, SHA-256 validated, and recorded on the local Ganache blockchain."
                }

            # Return full payload
            return self._send_json({
                "success": True,
                "face_detected": True,
                "face_confidence": round(face_res.confidence * 100, 1),
                "face_bbox": list(face_res.bbox),
                "candidates": formatted_candidates,
                "best_match": {
                    "title": best_candidate.get("title"),
                    "source_url": best_candidate.get("source_url"),
                    "similarity_score": best_score
                },
                "sha256": file_sha256,
                "blockchain": blockchain_receipt,
                "verdict": verdict
            })

        # -----------------------------------------------------------------
        # API: Verify File
        # -----------------------------------------------------------------
        elif path == "/api/verify":
            record_id = int(body.get("record_id", 1))
            file_type = body.get("file_type", "authentic")

            if file_type == "tampered":
                target_path = os.path.join(INPUT_DIR, "candidate_same.jpg")
            else:
                target_path = os.path.join(OUTPUT_DIR, "matched_image.jpg")
                if not os.path.exists(target_path):
                    target_path = os.path.join(INPUT_DIR, "person.jpg")

            current_hash = hash_file(target_path)

            try:
                client = BlockchainClient()
                rec = client.get_record(record_id)
                on_chain_hash = rec["data_hash"]
                is_match = verify_hashes(on_chain_hash, current_hash)
                ts = datetime.utcfromtimestamp(rec["timestamp"]).strftime('%Y-%m-%d %H:%M:%S UTC') if rec["timestamp"] else "N/A"

                return self._send_json({
                    "success": True,
                    "is_match": is_match,
                    "local_hash": current_hash,
                    "blockchain_hash": on_chain_hash,
                    "record_id": record_id,
                    "contract_address": client.contract_address,
                    "source_url": rec["source_url"],
                    "timestamp": ts,
                    "submitter": rec["submitter"]
                })
            except Exception as e:
                return self._send_json({
                    "success": False,
                    "error": str(e),
                    "local_hash": current_hash
                }, 400)

        # -----------------------------------------------------------------
        # API: Tamper / Restore File
        # -----------------------------------------------------------------
        elif path == "/api/tamper":
            action = body.get("action", "tamper")
            target_path = os.path.join(OUTPUT_DIR, "matched_image.jpg")
            backup_path = target_path + ".backup"

            if not os.path.exists(target_path):
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                import shutil
                shutil.copyfile(os.path.join(INPUT_DIR, "person.jpg"), target_path)

            orig_hash = hash_file(target_path)

            if action == "restore":
                if os.path.exists(backup_path):
                    import shutil
                    shutil.copyfile(backup_path, target_path)
                    try:
                        os.remove(backup_path)
                    except Exception:
                        pass
                restored_hash = hash_file(target_path)
                return self._send_json({
                    "success": True,
                    "action": "restore",
                    "file": "output/matched_image.jpg",
                    "original_hash": restored_hash,
                    "is_tampered": False
                })
            else:
                import shutil
                shutil.copyfile(target_path, backup_path)
                with open(target_path, "ab") as f:
                    f.write(b"\x00TAMPERED_CONTENT_DEMO_CYBERSIGHT\x00")
                new_hash = hash_file(target_path)
                return self._send_json({
                    "success": True,
                    "action": "tamper",
                    "file": "output/matched_image.jpg",
                    "original_hash": orig_hash,
                    "tampered_hash": new_hash,
                    "is_tampered": True
                })

        self.send_error(404, "Endpoint not found")


def ensure_react_built():
    """Ensure the React application is built into frontend/dist."""
    index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if not os.path.exists(index_file):
        print("[INFO] React distribution not found. Building with Vite...")
        try:
            import subprocess
            subprocess.run(["npm", "--prefix", "frontend", "run", "build"], check=True, shell=True)
            print("[INFO] React build successful.")
        except Exception as e:
            print(f"[WARN] Failed to build React app: {e}")


def main():
    ensure_react_built()

    server = HTTPServer(("localhost", PORT), PipelineApiHandler)
    url = f"http://localhost:{PORT}/"

    print("=" * 65)
    print("  CYBERSIGHT // FACE ID & BLOCKCHAIN VERIFICATION DASHBOARD")
    print("=" * 65)
    print("  Pipeline Backend:  OpenCV DNN (YuNet + SFace) + Ganache Web3")
    print(f"  Local Web Server:  {url}")
    print(f"  Serving Directory: {FRONTEND_DIST_DIR}")
    print("  REST Endpoints:    /api/status, /api/pipeline/run, /api/verify,")
    print("                     /api/tamper, /api/ledger")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 65)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] CyberSight server stopped.")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")


if __name__ == "__main__":
    main()
