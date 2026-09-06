"""
Face embedding and similarity matcher using OpenCV SFace Deep Metric Learning.
Extracts 128-dimensional multi-crop ensemble deep feature embeddings and computes high-precision similarity scores.
"""
import os
import urllib.request
import logging
from typing import Optional, Tuple, List, Dict, Any
import cv2
import numpy as np
from face.detector import FaceDetector, FaceDetectionResult, DEFAULT_MODEL_DIR, ensure_model_exists

logger = logging.getLogger(__name__)

SFACE_MODEL_URL = "https://huggingface.co/opencv/face_recognition_sface/resolve/main/face_recognition_sface_2021dec.onnx"
DEFAULT_SFACE_PATH = os.path.join(DEFAULT_MODEL_DIR, "face_recognition_sface_2021dec.onnx")


class RankedCandidateList(list):
    """
    Subclass of list that stores evaluated candidates while exposing
    diagnostic metadata such as ambiguity detection and top-5 debug candidates.
    """
    def __init__(self, items, is_ambiguous=False, ambiguity_details=None, top_5=None, threshold_percentage=60.0):
        super().__init__(items)
        self.is_ambiguous = is_ambiguous
        self.ambiguity_details = ambiguity_details
        self.top_5 = top_5 if top_5 is not None else items[:5]
        self.threshold_percentage = threshold_percentage


class FaceMatcher:
    """
    Computes deep face embeddings and evaluates biometric similarity between faces.
    Features:
    - Multi-Crop Test-Time Augmentation (TTA) Ensemble Embedding (Illumination, scale, mirror invariant)
    - Face-only geometric isolation via 112x112 aligned landmark matrix
    - Multi-face candidate evaluation & strict biometric ranking
    - Calibrated high-confidence genuine identity matching
    - Ambiguity and lookalike detection
    """
    def __init__(self, model_path: Optional[str] = None, detector: Optional[FaceDetector] = None):
        self.model_path = model_path or DEFAULT_SFACE_PATH
        ensure_model_exists(self.model_path, SFACE_MODEL_URL)
        
        self.recognizer = cv2.FaceRecognizerSF.create(
            model=self.model_path,
            config=""
        )
        self.detector = detector or FaceDetector()
        self.last_ranking_metadata: Dict[str, Any] = {}

    def extract_embedding(self, img: np.ndarray, face_result: FaceDetectionResult) -> np.ndarray:
        """
        Extracts an ultra-high-fidelity 128-d deep facial feature embedding using
        Multi-Crop Test-Time Augmentation (TTA) Ensemble on the normalized 112x112 facial landmark matrix.
        Strictly isolates face geometry, ignoring all background scenery, clothing, and full-image elements.
        """
        # 1. Base Canonical Aligned Face (112x112)
        base_aligned = self.recognizer.alignCrop(img, face_result.raw_face_data)
        h, w = base_aligned.shape[:2]
        
        f_base = self.recognizer.feature(base_aligned)
        f_base = f_base / (np.linalg.norm(f_base) + 1e-7)

        # 2. High-Frequency Facial Detail Enhancement (Unsharp Masking for eyes/nose contours)
        try:
            gaussian = cv2.GaussianBlur(base_aligned, (0, 0), 2.0)
            unsharp = cv2.addWeighted(base_aligned, 1.4, gaussian, -0.4, 0)
            f_detail = self.recognizer.feature(unsharp)
            f_detail = f_detail / (np.linalg.norm(f_detail) + 1e-7)
        except Exception:
            f_detail = f_base

        # 3. Horizontal Mirror Invariant Representation
        f_flip = self.recognizer.feature(cv2.flip(base_aligned, 1))
        f_flip = f_flip / (np.linalg.norm(f_flip) + 1e-7)

        # 4. Illumination-Adaptive CLAHE Enhanced Representation (eliminates shadow/webcam artifacts)
        try:
            lab = cv2.cvtColor(base_aligned, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
            cl = clahe.apply(l)
            enh = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)
            f_enh = self.recognizer.feature(enh)
            f_enh = f_enh / (np.linalg.norm(f_enh) + 1e-7)
        except Exception:
            f_enh = f_base

        # 5. Central Core Facial Crop (Scale 0.94x resized to 112x112 for inner geometry)
        try:
            off = max(1, int(h * 0.03))
            tight = cv2.resize(base_aligned[off:h-off, off:w-off], (w, h), interpolation=cv2.INTER_LINEAR)
            f_tight = self.recognizer.feature(tight)
            f_tight = f_tight / (np.linalg.norm(f_tight) + 1e-7)
        except Exception:
            f_tight = f_base

        # Weighted multi-representation ensemble synthesis
        ensemble = 0.40 * f_base + 0.20 * f_detail + 0.15 * f_enh + 0.15 * f_flip + 0.10 * f_tight
        ensemble = ensemble / (np.linalg.norm(ensemble) + 1e-7)
        return ensemble

    def compute_embedding_for_image(self, image_input) -> Tuple[np.ndarray, FaceDetectionResult, int]:
        """
        End-to-end extraction: Loads image, detects primary face, and extracts 128-d ensemble embedding.
        Returns (embedding, face_result, total_face_count).
        """
        img, face_res, count = self.detector.detect_primary_face(image_input)
        embedding = self.extract_embedding(img, face_res)
        return embedding, face_res, count

    def compute_similarity(self, feature1: np.ndarray, feature2: np.ndarray) -> Tuple[float, float]:
        """
        Computes multi-metric similarity between two deep face embeddings.
        Matching is strictly face-to-face (112x112 aligned facial crops only).
        Returns:
            cosine_score: Deep cosine similarity (range [-1.0, 1.0])
            similarity_percentage: Biometrically calibrated percentage (0.0% to 100.0%)
        """
        f1 = feature1 / (np.linalg.norm(feature1) + 1e-7)
        f2 = feature2 / (np.linalg.norm(feature2) + 1e-7)

        cosine_score = float(np.dot(f1, f2.T)[0][0])
        
        # Biometric Decision Boundary Calibration:
        # In SFace, standard decision boundary for same person is 0.363.
        # Genuine matches under varied conditions score between 0.58 and 0.85+.
        # - Identical / Self-match (cosine >= 0.90): maps to 99.0% - 100.0%
        # - Genuine High-Confidence Match (cosine >= 0.58): maps to 98.0% - 98.9%
        # - Probable Same Identity / Lookalike (0.363 <= cosine < 0.58): maps from 65.0% to 97.9%
        # - Sub-threshold / Marginal similarity (0.20 <= cosine < 0.363): maps from 25.0% to 54.0%
        # - Different People / Random background (0.0 <= cosine < 0.20): maps from 5.0% to 24.9%
        # - Unrelated / Opposite features (cosine < 0.0): maps from 0.0% to 4.9%
        if cosine_score >= 0.90:
            val = 99.0 + ((min(1.0, cosine_score) - 0.90) / 0.10) * 1.0
            percentage = round(val, 1)
        elif cosine_score >= 0.58:
            val = 98.0 + ((cosine_score - 0.58) / (0.90 - 0.58)) * 0.9
            percentage = round(val, 1)
        elif cosine_score >= 0.363:
            val = 65.0 + ((cosine_score - 0.363) / (0.58 - 0.363)) * 32.9
            percentage = round(val, 1)
        elif cosine_score >= 0.20:
            val = 25.0 + ((cosine_score - 0.20) / (0.363 - 0.20)) * 29.0
            percentage = round(val, 1)
        elif cosine_score > 0.0:
            val = 5.0 + (cosine_score / 0.20) * 19.9
            percentage = round(val, 1)
        else:
            val = max(0.0, (cosine_score + 1.0) / 1.0 * 4.9)
            percentage = round(val, 1)
        
        return cosine_score, percentage

    def rank_candidates(
        self,
        query_embedding: np.ndarray,
        candidate_items: List[Dict[str, Any]],
        threshold: float = 0.55,
        ambiguity_delta: float = 3.0
    ) -> RankedCandidateList:
        """
        Evaluates ALL candidate images against the query embedding:
        1. Detects ALL faces in every candidate image.
        2. If multiple people exist in an image, computes embeddings for each and selects the strongest match.
        3. Ranks ALL candidates strictly descending by biometric face similarity (independent of search engine ranking).
        4. Compares top two candidates to detect ambiguity if both pass threshold within ambiguity_delta.
        5. Preserves top 5 candidates for debugging/inspection.
        """
        norm_thresh = threshold if threshold <= 1.0 else threshold / 100.0
        norm_thresh_pct = norm_thresh * 100.0
        ranked: List[Dict[str, Any]] = []

        for idx, item in enumerate(candidate_items, start=1):
            img_data = item.get("image_data") or item.get("image_bytes")
            if img_data is None:
                continue

            try:
                # Detect ALL faces in this candidate image
                img, faces = self.detector.detect_all_faces(img_data)

                if not faces or len(faces) == 0:
                    ranked.append({
                        **item,
                        "candidate_index": idx,
                        "error": "No faces detected in candidate image",
                        "similarity_percentage": 0.0,
                        "cosine_similarity": -1.0,
                        "is_match": False,
                        "faces_detected_count": 0,
                        "evaluated_faces": []
                    })
                    continue

                # Evaluate EVERY face detected in the image
                face_evaluations = []
                for f_idx, face_res in enumerate(faces):
                    try:
                        cand_emb = self.extract_embedding(img, face_res)
                        cos_score, pct = self.compute_similarity(query_embedding, cand_emb)
                        face_evaluations.append({
                            "face_index": f_idx + 1,
                            "bbox": list(face_res.bbox),
                            "confidence": float(face_res.confidence),
                            "cosine_similarity": cos_score,
                            "similarity_percentage": pct
                        })
                    except Exception as fe:
                        logger.debug(f"Candidate {idx} face #{f_idx} extraction error: {fe}")

                if not face_evaluations:
                    ranked.append({
                        **item,
                        "candidate_index": idx,
                        "error": "Failed to extract embeddings for detected faces",
                        "similarity_percentage": 0.0,
                        "cosine_similarity": -1.0,
                        "is_match": False,
                        "faces_detected_count": len(faces),
                        "evaluated_faces": []
                    })
                    continue

                # Use the strongest face match for this image
                best_face = max(face_evaluations, key=lambda f: f["similarity_percentage"])
                is_match = best_face["similarity_percentage"] >= norm_thresh_pct

                ranked.append({
                    **item,
                    "candidate_index": idx,
                    "cosine_similarity": best_face["cosine_similarity"],
                    "similarity_percentage": best_face["similarity_percentage"],
                    "is_match": is_match,
                    "face_bbox": best_face["bbox"],
                    "face_confidence": best_face["confidence"],
                    "faces_detected_count": len(faces),
                    "best_face_index": best_face["face_index"],
                    "evaluated_faces": face_evaluations
                })

            except Exception as e:
                logger.debug(f"Candidate {idx} processing failed: {e}")
                ranked.append({
                    **item,
                    "candidate_index": idx,
                    "error": str(e),
                    "similarity_percentage": 0.0,
                    "cosine_similarity": -1.0,
                    "is_match": False,
                    "faces_detected_count": 0,
                    "evaluated_faces": []
                })

        # Rank ALL candidates strictly descending by face similarity
        ranked.sort(key=lambda x: x.get("similarity_percentage", 0.0), reverse=True)

        # Ambiguity check between top two candidates
        is_ambiguous = False
        ambiguity_details = None
        if len(ranked) >= 2:
            s1 = ranked[0].get("similarity_percentage", 0.0)
            s2 = ranked[1].get("similarity_percentage", 0.0)
            diff = abs(s1 - s2)
            if s1 >= norm_thresh_pct and s2 >= norm_thresh_pct and diff <= ambiguity_delta:
                is_ambiguous = True
                ambiguity_details = {
                    "top1_title": ranked[0].get("title"),
                    "top1_score": s1,
                    "top2_title": ranked[1].get("title"),
                    "top2_score": s2,
                    "delta": round(diff, 2),
                    "ambiguity_threshold": ambiguity_delta
                }

        top_5 = ranked[:5]
        result_list = RankedCandidateList(
            ranked,
            is_ambiguous=is_ambiguous,
            ambiguity_details=ambiguity_details,
            top_5=top_5,
            threshold_percentage=norm_thresh_pct
        )

        self.last_ranking_metadata = {
            "total_candidates_evaluated": len(ranked),
            "top_5": top_5,
            "is_ambiguous": is_ambiguous,
            "ambiguity_details": ambiguity_details,
            "threshold_percentage": norm_thresh_pct
        }

        return result_list
