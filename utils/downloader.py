"""
Safe Image Downloader and Metadata Storage.
Fetches candidate images from web URLs and persists winning matches with metadata.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, Tuple
import requests

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when an image download fails or content is invalid."""
    pass


class ImageDownloader:
    """
    Handles downloading and local persistence of web images.
    """
    def __init__(self, timeout: int = 7, max_size_bytes: int = 20 * 1024 * 1024):
        self.timeout = timeout
        self.max_size_bytes = max_size_bytes
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        }

    def download_image_bytes(self, url: str, timeout: Optional[int] = None) -> bytes:
        """
        Downloads image bytes from a URL with safety checks.
        Supports HTTP(S) URLs, data URIs, and local file paths.
        """
        if not url:
            raise DownloadError("Empty URL provided.")

        req_timeout = timeout or self.timeout

        # Local file path support
        if os.path.isfile(url):
            try:
                with open(url, "rb") as f:
                    return f.read()
            except Exception as e:
                raise DownloadError(f"Failed to read local file {url}: {e}")

        # Relative paths (e.g., /output/... or /input/...)
        if url.startswith("/") or url.startswith("input/") or url.startswith("output/"):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            local_path = os.path.join(base_dir, url.lstrip("/"))
            if os.path.isfile(local_path):
                try:
                    with open(local_path, "rb") as f:
                        return f.read()
                except Exception as e:
                    raise DownloadError(f"Failed to read local path {local_path}: {e}")

        # Data URI support
        if url.startswith("data:image/"):
            try:
                import base64
                header, b64data = url.split(",", 1)
                return base64.b64decode(b64data)
            except Exception as e:
                raise DownloadError(f"Failed to decode data URI: {e}")

        if not (url.startswith("http://") or url.startswith("https://")):
            raise DownloadError(f"Invalid URL schema: {url}")

        try:
            resp = requests.get(url, headers=self.headers, timeout=req_timeout, stream=True)
        except requests.RequestException as e:
            raise DownloadError(f"Connection error downloading {url}: {e}")

        if resp.status_code != 200:
            raise DownloadError(f"HTTP {resp.status_code} while downloading {url}")

        # Check content length if available
        cl = resp.headers.get("Content-Length")
        if cl and int(cl) > self.max_size_bytes:
            raise DownloadError(f"Image exceeds max size ({cl} > {self.max_size_bytes} bytes)")

        # Read content
        content = resp.content
        if len(content) == 0:
            raise DownloadError("Downloaded empty content.")

        # Basic magic bytes check for common image formats
        is_jpeg = content.startswith(b"\xff\xd8\xff")
        is_png = content.startswith(b"\x89PNG\r\n\x1a\n")
        is_webp = len(content) > 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP"
        is_gif = content.startswith(b"GIF87a") or content.startswith(b"GIF89a")
        
        # In case server serves with different header or minor format variations
        content_type = resp.headers.get("Content-Type", "")
        if not (is_jpeg or is_png or is_webp or is_gif or "image" in content_type.lower()):
            raise DownloadError(f"Downloaded content is not a recognized image format (Content-Type: {content_type})")

        return content

    def download_candidates_parallel(self, candidate_list: list, max_workers: int = 10, timeout: int = 6) -> list:
        """
        Concurrently downloads image bytes for candidate items with fast failover.
        """
        import concurrent.futures

        def _fetch_candidate(cand):
            target_url = getattr(cand, "image_url", None) or getattr(cand, "thumbnail_url", None)
            if not target_url and isinstance(cand, dict):
                target_url = cand.get("image_url") or cand.get("thumbnail_url")
            
            if not target_url:
                return None

            # Try primary image URL then thumbnail if primary fails
            for u in [target_url, getattr(cand, "thumbnail_url", None) if hasattr(cand, "thumbnail_url") else (cand.get("thumbnail_url") if isinstance(cand, dict) else None)]:
                if not u:
                    continue
                try:
                    data = self.download_image_bytes(u, timeout=timeout)
                    if data and len(data) > 200:
                        return {
                            "title": getattr(cand, "title", None) if hasattr(cand, "title") else cand.get("title", "Discovered Candidate"),
                            "source_url": getattr(cand, "source_url", None) if hasattr(cand, "source_url") else cand.get("source_url", u),
                            "image_url": target_url,
                            "thumbnail_url": u,
                            "image_bytes": data,
                            "image_data": data,
                            "platform": getattr(cand, "platform", None) if hasattr(cand, "platform") else cand.get("platform", "web"),
                            "engine": getattr(cand, "engine", None) if hasattr(cand, "engine") else cand.get("engine", "web_discovery")
                        }
                except Exception:
                    continue
            return None

        evaluated = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_cand = {executor.submit(_fetch_candidate, c): c for c in candidate_list}
            for future in concurrent.futures.as_completed(future_to_cand):
                try:
                    res = future.result()
                    if res is not None:
                        evaluated.append(res)
                except Exception:
                    pass

        return evaluated

    def save_image(self, data: bytes, destination_path: str) -> str:
        """
        Saves raw bytes to the specified path, creating directories if needed.
        """
        dir_name = os.path.dirname(os.path.abspath(destination_path))
        os.makedirs(dir_name, exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(data)
        return destination_path

    def save_metadata(self, metadata: Dict[str, Any], destination_path: str) -> str:
        """
        Saves metadata dictionary as a formatted JSON file.
        """
        dir_name = os.path.dirname(os.path.abspath(destination_path))
        os.makedirs(dir_name, exist_ok=True)
        with open(destination_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        return destination_path
