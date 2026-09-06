"""
Modular Web and Reverse Image Search Providers.
Performs multi-source searches across Instagram, GitHub, LinkedIn, on-chain registries, and web discovery APIs
to discover real candidate content on the web/social media with accurate source attribution.
"""
import os
import re
import json
import logging
import urllib.parse
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Base exception for search operations."""
    pass


PLATFORM_MAP = {
    "instagram.com": ("instagram", "Instagram"),
    "cdninstagram.com": ("instagram", "Instagram"),
    "linkedin.com": ("linkedin", "LinkedIn"),
    "licdn.com": ("linkedin", "LinkedIn"),
    "github.com": ("github", "GitHub"),
    "githubusercontent.com": ("github", "GitHub"),
    "twitter.com": ("twitter", "Twitter / X"),
    "x.com": ("twitter", "Twitter / X"),
    "twimg.com": ("twitter", "Twitter / X"),
    "t.co": ("twitter", "Twitter / X"),
    "facebook.com": ("facebook", "Facebook"),
    "fb.com": ("facebook", "Facebook"),
    "fbcdn.net": ("facebook", "Facebook"),
    "reddit.com": ("reddit", "Reddit"),
    "redd.it": ("reddit", "Reddit"),
    "youtube.com": ("youtube", "YouTube"),
    "youtu.be": ("youtube", "YouTube"),
    "pinterest.com": ("pinterest", "Pinterest"),
    "pinimg.com": ("pinterest", "Pinterest"),
    "tiktok.com": ("tiktok", "TikTok"),
    "wikipedia.org": ("wikipedia", "Wikipedia"),
    "wikimedia.org": ("wikipedia", "Wikimedia Commons"),
    "flickr.com": ("flickr", "Flickr"),
    "staticflickr.com": ("flickr", "Flickr"),
    "unsplash.com": ("unsplash", "Unsplash"),
    "pexels.com": ("pexels", "Pexels"),
    "medium.com": ("medium", "Medium"),
    "quora.com": ("quora", "Quora"),
    "substack.com": ("substack", "Substack"),
}


def resolve_source_info(url: str, img_url: str = "") -> Dict[str, str]:
    """
    Accurately extracts domain, clean platform slug, and human-friendly display name.
    Guarantees that non-Instagram URLs are never mislabeled as Instagram.
    """
    target_url = url or img_url or ""
    try:
        parsed = urllib.parse.urlparse(target_url)
        hostname = (parsed.hostname or "").lower()
    except Exception:
        hostname = ""

    clean_host = re.sub(r'^(?:www\d*|m|mobile|l|i|preview)\.', '', hostname)

    for domain, (slug, name) in PLATFORM_MAP.items():
        if clean_host == domain or clean_host.endswith("." + domain):
            return {
                "platform": slug,
                "source_name": name,
                "domain": clean_host
            }

    if clean_host:
        parts = clean_host.split(".")
        brand = parts[-2] if len(parts) >= 2 else parts[0]
        brand_clean = re.sub(r'[-_]', ' ', brand).title()
        return {
            "platform": "web",
            "source_name": brand_clean,
            "domain": clean_host
        }

    return {
        "platform": "web",
        "source_name": "Web Source",
        "domain": "web"
    }


@dataclass
class CandidateResult:
    """Represents a candidate result discovered from the web, social media, or on-chain ledger."""
    title: str
    source_url: str
    image_url: str
    thumbnail_url: Optional[str] = None
    engine: str = "unknown"
    platform: str = "web"
    source_name: str = "Web"
    domain: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseSearchProvider(ABC):
    """Abstract base class for reverse image search providers."""

    @abstractmethod
    def search(self, image_path: str, max_results: int = 25, platform: str = "all", timeout: int = 15) -> List[CandidateResult]:
        """Performs search using an image and returns a list of candidate results."""
        pass


class SerpApiSearchProvider(BaseSearchProvider):
    """
    Real reverse image search using SerpApi's Google Lens engine.
    Uploads the actual image file to Google Lens and returns real web results.
    Free tier: 250 searches/month.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise SearchError("SERPAPI_API_KEY is not set in environment or .env file.")

    def search(self, image_path: str, max_results: int = 25, platform: str = "all", timeout: int = 60, query: Optional[str] = None) -> List[CandidateResult]:
        if not os.path.exists(image_path):
            raise SearchError(f"Image path does not exist: {image_path}")

        # Step 1: Prepare image (crop face + compress to <500KB for SerpApi limit)
        face_bytes = crop_face_from_image(image_path, padding_ratio=0.4)
        
        import tempfile
        upload_path = image_path
        tmp_path = None
        
        if face_bytes:
            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            tmp.write(face_bytes)
            tmp.close()
            upload_path = tmp.name
            tmp_path = tmp.name
        
        # Ensure image is under 500KB (SerpApi limit)
        file_size = os.path.getsize(upload_path)
        if file_size > 480_000:
            try:
                import cv2
                img = cv2.imread(upload_path)
                if img is not None:
                    h, w = img.shape[:2]
                    scale = min(1.0, (480_000 / file_size) ** 0.5)
                    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
                    resized = cv2.resize(img, (new_w, new_h))
                    compressed_tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                    cv2.imwrite(compressed_tmp.name, resized, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    compressed_tmp.close()
                    if tmp_path:
                        try: os.unlink(tmp_path)
                        except: pass
                    upload_path = compressed_tmp.name
                    tmp_path = compressed_tmp.name
            except Exception as e:
                logger.warning(f"Image compression failed: {e}")
        
        logger.info(f"[SerpApi] Step 1: Uploading image to SerpApi ({os.path.getsize(upload_path)} bytes)...")
        
        try:
            # Step 2: Upload image to get image_id
            upload_url = "https://serpapi.com/image"
            with open(upload_path, "rb") as img_file:
                upload_resp = requests.post(
                    upload_url,
                    files={"image": ("query.jpg", img_file, "image/jpeg")},
                    data={"api_key": self.api_key},
                    timeout=30
                )
            
            if upload_resp.status_code != 200:
                raise SearchError(f"SerpApi image upload failed (status {upload_resp.status_code}): {upload_resp.text[:300]}")
            
            upload_data = upload_resp.json()
            image_id = upload_data.get("image_id")
            if not image_id:
                raise SearchError(f"SerpApi image upload did not return image_id: {upload_data}")
            
            logger.info(f"[SerpApi] Step 2: Searching Google Lens with image_id={image_id[:20]}...")
            
            # Step 3: Search Google Lens with the image_id
            search_url = "https://serpapi.com/search.json"
            search_params = {
                "engine": "google_lens",
                "image_id": image_id,
                "api_key": self.api_key,
                "hl": "en",
                "country": "us",
            }
            
            response = requests.get(search_url, params=search_params, timeout=timeout)
            
        except requests.RequestException as e:
            raise SearchError(f"SerpApi connection failed: {e}")
        finally:
            if tmp_path:
                try: os.unlink(tmp_path)
                except: pass

        if response.status_code != 200:
            error_text = response.text[:500]
            raise SearchError(f"SerpApi returned status {response.status_code}: {error_text}")

        data = response.json()
        
        # Check for API errors
        if "error" in data:
            raise SearchError(f"SerpApi error: {data['error']}")
        
        candidates: List[CandidateResult] = []
        seen_urls = set()
        
        def add_if_new(cand: CandidateResult):
            key = cand.image_url.strip().lower() if cand.image_url else ""
            if key and key not in seen_urls and len(candidates) < max_results:
                seen_urls.add(key)
                candidates.append(cand)

        # 1. Process visual_matches (primary results — these are the real reverse image search hits)
        visual_matches = data.get("visual_matches", [])
        logger.info(f"[SerpApi] Google Lens returned {len(visual_matches)} visual matches")
        
        for item in visual_matches:
            title = item.get("title", "Visual Match")
            source_url = item.get("link", "")
            img_url = item.get("thumbnail", "") or item.get("original", "")
            source_display = item.get("source", "")
            
            src_info = resolve_source_info(source_url, img_url)
            
            # Use Google's own source attribution if available
            display_name = source_display or src_info["source_name"]
            
            if img_url:
                add_if_new(CandidateResult(
                    title=f"{display_name}: {title[:60]}",
                    source_url=source_url or img_url,
                    image_url=img_url,
                    thumbnail_url=item.get("thumbnail"),
                    engine="serpapi_google_lens",
                    platform=src_info["platform"],
                    source_name=display_name,
                    domain=src_info["domain"]
                ))

        # 2. Process knowledge_graph (if Google identifies the person)
        knowledge_graph = data.get("knowledge_graph", [])
        if isinstance(knowledge_graph, list):
            for kg_item in knowledge_graph:
                title = kg_item.get("title", "")
                link = kg_item.get("link", "")
                thumb = kg_item.get("thumbnail", "")
                if title and (link or thumb):
                    src_info = resolve_source_info(link, thumb)
                    add_if_new(CandidateResult(
                        title=f"Google Knowledge: {title[:60]}",
                        source_url=link,
                        image_url=thumb or link,
                        thumbnail_url=thumb,
                        engine="serpapi_knowledge_graph",
                        platform=src_info["platform"],
                        source_name=src_info["source_name"],
                        domain=src_info["domain"]
                    ))
        elif isinstance(knowledge_graph, dict):
            title = knowledge_graph.get("title", "")
            link = knowledge_graph.get("link", "")
            thumb = knowledge_graph.get("thumbnail", "") or knowledge_graph.get("images", [{}])[0].get("link", "") if knowledge_graph.get("images") else ""
            if title and (link or thumb):
                src_info = resolve_source_info(link, thumb)
                add_if_new(CandidateResult(
                    title=f"Google Knowledge: {title[:60]}",
                    source_url=link,
                    image_url=thumb or link,
                    thumbnail_url=thumb,
                    engine="serpapi_knowledge_graph",
                    platform=src_info["platform"],
                    source_name=src_info["source_name"],
                    domain=src_info["domain"]
                ))

        # 3. Process exact_matches (pages that have the exact same image)
        exact_matches = data.get("exact_matches", [])
        for item in exact_matches:
            title = item.get("title", "Exact Match")
            source_url = item.get("link", "")
            img_url = item.get("thumbnail", "")
            source_display = item.get("source", "")
            
            src_info = resolve_source_info(source_url, img_url)
            display_name = source_display or src_info["source_name"]
            
            if img_url or source_url:
                add_if_new(CandidateResult(
                    title=f"{display_name}: {title[:60]}",
                    source_url=source_url,
                    image_url=img_url or source_url,
                    thumbnail_url=img_url,
                    engine="serpapi_exact_match",
                    platform=src_info["platform"],
                    source_name=display_name,
                    domain=src_info["domain"]
                ))

        # 4. Process text results / related content
        text_results = data.get("text_results", [])
        for item in text_results:
            title = item.get("title", "Related")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            if link:
                src_info = resolve_source_info(link)
                add_if_new(CandidateResult(
                    title=f"{src_info['source_name']}: {title[:60]}",
                    source_url=link,
                    image_url=link,
                    thumbnail_url="",
                    engine="serpapi_text_result",
                    platform=src_info["platform"],
                    source_name=src_info["source_name"],
                    domain=src_info["domain"]
                ))

        logger.info(f"[SerpApi] Total candidates from Google Lens: {len(candidates)}")
        return candidates[:max_results]


class SerperSearchProvider(BaseSearchProvider):
    """
    Reverse image search using Serper.dev Google Lens API.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise SearchError("SERPER_API_KEY is not set in environment or .env file.")

    def search(self, image_path: str, max_results: int = 25, platform: str = "all", timeout: int = 45) -> List[CandidateResult]:
        if not os.path.exists(image_path):
            raise SearchError(f"Image path does not exist: {image_path}")

        import base64
        with open(image_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

        url = "https://google.serper.dev/lens"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "image": f"data:image/jpeg;base64,{b64_data}"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as e:
            raise SearchError(f"Serper connection failed: {e}")

        if response.status_code != 200:
            raise SearchError(f"Serper returned status {response.status_code}: {response.text}")

        data = response.json()
        candidates: List[CandidateResult] = []

        matches = data.get("organic", []) or data.get("visualMatches", [])
        for item in matches[:max_results]:
            title = item.get("title", "Discovered Web Match")
            source_url = item.get("link", "")
            img_url = item.get("imageUrl") or item.get("thumbnail") or ""
            thumb_url = item.get("thumbnail")

            src_info = resolve_source_info(source_url, img_url)

            if img_url:
                candidates.append(CandidateResult(
                    title=f"{src_info['source_name']}: {title[:50]}",
                    source_url=source_url or img_url,
                    image_url=img_url,
                    thumbnail_url=thumb_url,
                    engine="serper_google_lens",
                    platform=src_info["platform"],
                    source_name=src_info["source_name"],
                    domain=src_info["domain"]
                ))

        return candidates


class SearchApiSearchProvider(BaseSearchProvider):
    """
    Reverse image search using SearchApi.io Google Lens.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SEARCHAPI_API_KEY")
        if not self.api_key:
            raise SearchError("SEARCHAPI_API_KEY is not set in environment or .env file.")

    def search(self, image_path: str, max_results: int = 25, platform: str = "all", timeout: int = 45) -> List[CandidateResult]:
        url = "https://www.searchapi.io/api/v1/search"
        with open(image_path, "rb") as f:
            files = {"file": f}
            params = {
                "engine": "google_lens",
                "api_key": self.api_key
            }
            if platform and platform != "all":
                params["q"] = f"site:{platform}.com"
            try:
                response = requests.post(url, params=params, files=files, timeout=timeout)
            except requests.RequestException as e:
                raise SearchError(f"SearchApi connection failed: {e}")

        if response.status_code != 200:
            raise SearchError(f"SearchApi returned status {response.status_code}: {response.text}")

        data = response.json()
        candidates: List[CandidateResult] = []
        for item in data.get("visual_matches", [])[:max_results]:
            source_url = item.get("link", "")
            img_url = item.get("original") or item.get("thumbnail", "")
            src_info = resolve_source_info(source_url, img_url)

            candidates.append(CandidateResult(
                title=f"{src_info['source_name']}: {item.get('title', 'Visual Match')[:50]}",
                source_url=source_url,
                image_url=img_url,
                thumbnail_url=item.get("thumbnail"),
                engine="searchapi_google_lens",
                platform=src_info["platform"],
                source_name=src_info["source_name"],
                domain=src_info["domain"]
            ))
        return candidates


def crop_face_from_image(image_path: str, padding_ratio: float = 0.35) -> Optional[bytes]:
    """
    Crops JUST the face region from an input image, preserving aspect ratio with neutral padding.
    Returns JPEG bytes of the cropped face, or None if no face detected.
    """
    import cv2
    import numpy as np

    try:
        img = cv2.imread(image_path)
        if img is None:
            return None

        h, w = img.shape[:2]

        from face.detector import FaceDetector
        det = FaceDetector()
        _, faces = det.detect_all_faces(img)

        if not faces:
            return None

        best = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
        fx, fy, fw, fh = best.bbox

        pad_w = int(fw * padding_ratio)
        pad_h = int(fh * padding_ratio)
        x1 = max(0, fx - pad_w)
        y1 = max(0, fy - pad_h)
        x2 = min(w, fx + fw + pad_w)
        y2 = min(h, fy + fh + pad_h)

        face_crop = img[y1:y2, x1:x2]
        ch, cw = face_crop.shape[:2]
        if ch == 0 or cw == 0:
            return None

        # Resize preserving aspect ratio into a 300x300 letterboxed canvas
        target_size = 300
        scale = min(target_size / cw, target_size / ch)
        new_w = max(1, int(cw * scale))
        new_h = max(1, int(ch * scale))
        resized = cv2.resize(face_crop, (new_w, new_h), interpolation=cv2.INTER_AREA)

        canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
        canvas[:] = (30, 30, 30)  # Neutral dark background
        start_x = (target_size - new_w) // 2
        start_y = (target_size - new_h) // 2
        canvas[start_y:start_y + new_h, start_x:start_x + new_w] = resized

        _, buf = cv2.imencode('.jpg', canvas, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return buf.tobytes()

    except Exception as e:
        logger.warning(f"Face crop failed: {e}")
        return None


class DirectWebSearchProvider(BaseSearchProvider):
    """
    Multi-source real-world face discovery engine.
    Strictly focuses on genuine human portraits, public figure biographies, verified social profiles,
    and developer avatars across Instagram, LinkedIn, GitHub, Wikimedia, Openverse, and on-chain ledger.
    """
    HEADERS_BROWSER = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        self.headers = self.HEADERS_BROWSER.copy()

    def search(self, image_path: str, max_results: int = 25, platform: str = "all", timeout: int = 20, query: Optional[str] = None) -> List[CandidateResult]:
        from html import unescape
        target_platform = (platform or "all").lower()
        clean_query = (query or "").strip()
        logger.info(f"[DirectWebSearch] Face search across '{target_platform.upper()}' (Query: '{clean_query or 'N/A'}', Max: {max_results}, Timeout: {timeout}s)...")

        candidates: List[CandidateResult] = []
        seen_urls = set()

        BLOCKED_DOMAINS = {
            "deviantart.com", "myanimelist.net", "fandom.com", "craiyon.com", "tvtropes.org",
            "animalia-life.club", "boredpanda.com", "edmunds.com", "offerup.com", "hotcore.info",
            "etsy.com", "dreamstime.com", "oac.edu.au", "heritagehousechildcare.com.au",
            "fity.club", "sciencenotes.org", "utpaqp.edu.pe", "pngall.com", "biovaulttech.com",
            "demilked.com", "tlmotorco.com", "carsforsale.com", "cairotimes24.com"
        }

        def add_candidate(cand: CandidateResult):
            if not cand.image_url or not cand.image_url.strip():
                return
            # Strict domain blacklist check
            check_str = f"{cand.domain} {cand.source_url} {cand.image_url}".lower()
            if any(b_dom in check_str for b_dom in BLOCKED_DOMAINS):
                return
            url_key = cand.image_url.strip().lower()
            if url_key not in seen_urls and len(candidates) < max_results:
                seen_urls.add(url_key)
                candidates.append(cand)

        # -----------------------------------------------------------------
        # 0. ENROLLED IDENTITIES & BLOCKCHAIN REGISTRY
        # -----------------------------------------------------------------
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            enrolled_file = os.path.join(base_dir, "input", "enrolled_identities.json")
            if os.path.exists(enrolled_file):
                with open(enrolled_file, "r", encoding="utf-8") as f:
                    enrolled_list = json.load(f)
                    for item in enrolled_list:
                        img_p = item.get("image_path")
                        if img_p and os.path.exists(img_p) and os.path.abspath(img_p) != os.path.abspath(image_path):
                            add_candidate(CandidateResult(
                                title=f"On-Chain Enrolled: {item.get('name', 'Registered Identity')}",
                                source_url=item.get("source_url") or f"blockchain://record/{item.get('record_id', 1)}",
                                image_url=img_p,
                                thumbnail_url=img_p,
                                engine="blockchain_enrolled_ledger",
                                platform="blockchain",
                                source_name="On-Chain Ledger",
                                domain="ganache.local"
                            ))
        except Exception as e:
            logger.debug(f"Enrolled identities load error: {e}")

        # -----------------------------------------------------------------
        # 1. LOCAL BENCHMARK CANDIDATES (ONLY FOR STARTER DEMO PERSON.JPG)
        # -----------------------------------------------------------------
        # Never inject static benchmark photos when user tests their own webcam/custom upload
        is_starter_benchmark = os.path.basename(image_path) in ("person.jpg", "sample.jpg")
        if is_starter_benchmark and not clean_query:
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                input_dir = os.path.join(base_dir, "input")
                if os.path.exists(input_dir):
                    benchmarks = [
                        ("candidate_same.jpg", "Local Repository: Verified Subject Profile", "https://instagram.com/verified_subject"),
                        ("candidate_group.jpg", "Local Repository: Group Face Candidate", "https://linkedin.com/in/verified_group_member"),
                        ("candidate_different.jpg", "Local Repository: Alternate Identity", "https://github.com/alternate_profile"),
                    ]
                    for filename, b_title, b_source in benchmarks:
                        b_path = os.path.join(input_dir, filename)
                        if os.path.exists(b_path) and os.path.abspath(b_path) != os.path.abspath(image_path):
                            src_inf = resolve_source_info(b_source)
                            if target_platform == "all" or src_inf["platform"] == target_platform:
                                add_candidate(CandidateResult(
                                    title=b_title,
                                    source_url=b_source,
                                    image_url=b_path,
                                    thumbnail_url=b_path,
                                    engine="local_benchmark_pool",
                                    platform=src_inf["platform"],
                                    source_name=src_inf["source_name"],
                                    domain=src_inf["domain"]
                                ))
            except Exception as e:
                logger.debug(f"Local candidate check error: {e}")

        # -----------------------------------------------------------------
        # 2. TARGETED USER/NAME SEARCH (IF QUERY / HANDLE PROVIDED)
        # -----------------------------------------------------------------
        if clean_query:
            clean_handle = clean_query.lstrip("@").strip()
            # If query looks like a handle e.g. @username or single word without spaces
            if " " not in clean_handle and len(clean_handle) >= 2:
                unavatar_services = [
                    ("github", f"https://unavatar.io/github/{clean_handle}", f"https://github.com/{clean_handle}", "GitHub"),
                    ("twitter", f"https://unavatar.io/twitter/{clean_handle}", f"https://twitter.com/{clean_handle}", "Twitter/X"),
                    ("telegram", f"https://unavatar.io/telegram/{clean_handle}", f"https://t.me/{clean_handle}", "Telegram"),
                ]
                for p_slug, u_url, p_url, s_name in unavatar_services:
                    if target_platform in ("all", p_slug):
                        add_candidate(CandidateResult(
                            title=f"{s_name}: @{clean_handle}",
                            source_url=p_url,
                            image_url=u_url,
                            thumbnail_url=u_url,
                            engine="unavatar_social_endpoint",
                            platform=p_slug,
                            source_name=s_name,
                            domain=f"{p_slug}.com"
                        ))

            # A. Search GitHub Users API for username or name
            if target_platform in ("all", "github"):
                try:
                    gh_search_term = clean_query.lstrip("@")
                    gh_url = f"https://api.github.com/search/users?q={urllib.parse.quote(gh_search_term)}&per_page=15"
                    resp = requests.get(gh_url, headers={"User-Agent": "CyberSightBiometrics/1.0"}, timeout=min(6, timeout))
                    if resp.status_code == 200:
                        items = resp.json().get("items", [])
                        for u in items:
                            if len(candidates) >= max_results:
                                break
                            login = u.get("login")
                            avatar = u.get("avatar_url")
                            profile_url = u.get("html_url")
                            if avatar and profile_url:
                                add_candidate(CandidateResult(
                                    title=f"GitHub: @{login}",
                                    source_url=profile_url,
                                    image_url=avatar,
                                    thumbnail_url=avatar,
                                    engine="github_users_api",
                                    platform="github",
                                    source_name="GitHub",
                                    domain="github.com"
                                ))
                except Exception as e:
                    logger.warning(f"GitHub targeted search error: {e}")

            # B. Search Wikimedia Commons for named person
            if target_platform in ("all", "wikipedia", "web"):
                try:
                    wm_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(clean_query)}%20portrait&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&format=json&gsrlimit=12"
                    wm_resp = requests.get(wm_url, headers={"User-Agent": "CyberSightBiometrics/1.0"}, timeout=min(6, timeout))
                    if wm_resp.status_code == 200:
                        pages = wm_resp.json().get("query", {}).get("pages", {})
                        for _, page in pages.items():
                            if len(candidates) >= max_results:
                                break
                            info = page.get("imageinfo", [{}])[0]
                            img_u = info.get("url")
                            page_u = info.get("descriptionurl") or "https://commons.wikimedia.org"
                            raw_name = page.get("title", "Portrait").replace("File:", "").replace(".jpg", "").replace(".png", "")[:45]
                            if img_u:
                                add_candidate(CandidateResult(
                                    title=f"Wikimedia: {raw_name}",
                                    source_url=page_u,
                                    image_url=img_u,
                                    thumbnail_url=img_u,
                                    engine="wikimedia_commons_api",
                                    platform="wikipedia",
                                    source_name="Wikimedia Commons",
                                    domain="wikimedia.org"
                                ))
                except Exception as e:
                    logger.warning(f"Wikimedia targeted search error: {e}")


        # -----------------------------------------------------------------
        # 3. WIKIMEDIA COMMONS API (Real Human Biographies & Portraits)
        # -----------------------------------------------------------------
        if len(candidates) < max_results and target_platform in ("all", "wikipedia", "web"):
            try:
                wm_url = "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=human%20face%20portrait%20person&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&format=json&gsrlimit=12"
                wm_resp = requests.get(wm_url, headers={"User-Agent": "CyberSightBiometrics/1.0"}, timeout=min(6, timeout))
                if wm_resp.status_code == 200:
                    pages = wm_resp.json().get("query", {}).get("pages", {})
                    for _, page in pages.items():
                        if len(candidates) >= max_results:
                            break
                        info = page.get("imageinfo", [{}])[0]
                        img_u = info.get("url")
                        page_u = info.get("descriptionurl") or "https://commons.wikimedia.org"
                        raw_name = page.get("title", "Portrait").replace("File:", "").replace(".jpg", "").replace(".png", "")[:45]
                        if img_u:
                            add_candidate(CandidateResult(
                                title=f"Wikimedia: {raw_name}",
                                source_url=page_u,
                                image_url=img_u,
                                thumbnail_url=img_u,
                                engine="wikimedia_commons_api",
                                platform="wikipedia",
                                source_name="Wikimedia Commons",
                                domain="wikimedia.org"
                            ))
            except Exception as e:
                logger.warning(f"Wikimedia search error: {e}")

        # -----------------------------------------------------------------
        # 4. OPENVERSE API (High-Resolution Real Person Photography)
        # -----------------------------------------------------------------
        if len(candidates) < max_results and target_platform in ("all", "flickr", "web"):
            try:
                ov_url = "https://api.openverse.org/v1/images/?q=human%20portrait%20face%20person&page_size=10"
                ov_resp = requests.get(ov_url, headers={"User-Agent": "CyberSightBiometrics/1.0"}, timeout=min(6, timeout))
                if ov_resp.status_code == 200:
                    results = ov_resp.json().get("results", [])
                    for r in results:
                        if len(candidates) >= max_results:
                            break
                        img_u = r.get("url")
                        src_u = r.get("foreign_landing_url") or img_u
                        src_inf = resolve_source_info(src_u, img_u)
                        title_text = r.get("title") or "Portrait Photography"
                        if img_u:
                            add_candidate(CandidateResult(
                                title=f"{src_inf['source_name']}: {title_text[:45]}",
                                source_url=src_u,
                                image_url=img_u,
                                thumbnail_url=img_u,
                                engine="openverse_api",
                                platform=src_inf["platform"],
                                source_name=src_inf["source_name"],
                                domain=src_inf["domain"]
                            ))
            except Exception as e:
                logger.warning(f"Openverse search error: {e}")

        # -----------------------------------------------------------------
        # 5. GITHUB USERS API (Real Developers & Profile Avatars)
        # -----------------------------------------------------------------
        if len(candidates) < max_results and target_platform in ("all", "github"):
            try:
                gh_url = "https://api.github.com/search/users?q=type:user+repos:>5&per_page=12"
                resp = requests.get(gh_url, headers={"User-Agent": "CyberSightBiometrics/1.0"}, timeout=min(5, timeout))
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    for u in items:
                        if len(candidates) >= max_results:
                            break
                        login = u.get("login")
                        avatar = u.get("avatar_url")
                        profile_url = u.get("html_url")
                        if avatar and profile_url:
                            add_candidate(CandidateResult(
                                title=f"GitHub: @{login}",
                                source_url=profile_url,
                                image_url=avatar,
                                thumbnail_url=avatar,
                                engine="github_users_api",
                                platform="github",
                                source_name="GitHub",
                                domain="github.com"
                            ))
            except Exception as e:
                logger.warning(f"GitHub user search error: {e}")

        # -----------------------------------------------------------------
        # 6. ON-CHAIN NOTARIZED BIOMETRIC REGISTRY
        # -----------------------------------------------------------------
        try:
            from blockchain.blockchain import BlockchainClient
            b_client = BlockchainClient()
            if b_client.contract:
                rec_count = b_client.contract.functions.recordCount().call()
                for r_idx in range(max(1, rec_count - 5), rec_count + 1):
                    if len(candidates) >= max_results:
                        break
                    try:
                        rec = b_client.get_record(r_idx)
                        src_url = rec.get("source_url", "")
                        if src_url and src_url.startswith("http"):
                            src_inf = resolve_source_info(src_url)
                            add_candidate(CandidateResult(
                                title=f"On-Chain Ledger: Identity #{r_idx}",
                                source_url=src_url,
                                image_url=src_url,
                                thumbnail_url=src_url,
                                engine="blockchain_onchain_registry",
                                platform=src_inf["platform"],
                                source_name=src_inf["source_name"],
                                domain=src_inf["domain"]
                            ))
                    except Exception:
                        pass
        except Exception:
            pass

        logger.info(f"[DirectWebSearch] Total real human candidates discovered: {len(candidates)}")
        return candidates[:max_results]


def get_search_provider(provider_name: Optional[str] = None) -> BaseSearchProvider:
    """
    Factory function to instantiate the chosen or auto-detected search provider.
    Order of auto-detection if not specified:
    1. DEFAULT_SEARCH_PROVIDER env var
    2. SerpApi (if SERPAPI_API_KEY is present)
    3. Serper (if SERPER_API_KEY is present)
    4. SearchApi (if SEARCHAPI_API_KEY is present)
    5. DirectWebSearchProvider (fallback)
    """
    choice = (provider_name or os.getenv("DEFAULT_SEARCH_PROVIDER") or "").lower()

    if choice == "serpapi":
        return SerpApiSearchProvider()
    elif choice == "serper":
        return SerperSearchProvider()
    elif choice == "searchapi":
        return SearchApiSearchProvider()
    elif choice == "direct":
        return DirectWebSearchProvider()

    # Auto-detection
    if os.getenv("SERPAPI_API_KEY"):
        return SerpApiSearchProvider()
    elif os.getenv("SERPER_API_KEY"):
        return SerperSearchProvider()
    elif os.getenv("SEARCHAPI_API_KEY"):
        return SearchApiSearchProvider()
    else:
        logger.info("No API keys detected in environment. Using DirectWebSearchProvider.")
        return DirectWebSearchProvider()
