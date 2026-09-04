"""
Face embedding and similarity matcher using OpenCV SFace.
Extracts 128-dimensional deep feature embeddings and computes cosine similarity scores.
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


class FaceMatcher:
    """
    Computes face embeddings and evaluates similarity between faces.
    """
    def __init__(self, model_path: Optional[str] = None, detector: Optional[FaceDetector] = None):
        self.model_path = model_path or DEFAULT_SFACE_PATH
        ensure_model_exists(self.model_path, SFACE_MODEL_URL)
        
        self.recognizer = cv2.FaceRecognizerSF.create(
            model=self.model_path,
            config=""
        )
        self.detector = detector or FaceDetector()

    def extract_embedding(self, img: np.ndarray, face_result: FaceDetectionResult) -> np.ndarray:
        """
        Aligns the detected face using its landmarks and extracts a 128-d feature embedding.
        """
        aligned_face = self.recognizer.alignCrop(img, face_result.raw_face_data)
        feature = self.recognizer.feature(aligned_face)
        return feature

    def compute_embedding_for_image(self, image_input) -> Tuple[np.ndarray, FaceDetectionResult, int]:
        """
        End-to-end extraction: Loads image, detects primary face, and extracts 128-d embedding.
        Returns (embedding, face_result, total_face_count).
        """
        img, face_res, count = self.detector.detect_primary_face(image_input)
        embedding = self.extract_embedding(img, face_res)
        return embedding, face_res, count

    def compute_similarity(self, feature1: np.ndarray, feature2: np.ndarray) -> Tuple[float, float]:
        """
        Computes cosine similarity and L2 distance between two face embeddings.
        Returns:
            cosine_similarity: Raw cosine score (range [-1, 1], higher is more similar)
            similarity_percentage: Normalized similarity percentage (0.0 to 100.0%)
        """
        cosine_score = float(self.recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE))
        l2_dist = float(self.recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_NORM_L2))
        
        # SFace cosine similarity is in [-1, 1]. In OpenCV benchmarks,
        # cosine score >= 0.363 is the decision boundary for identical face identity.
        # Calibrate similarity percentage to reflect biometric confidence accurately:
        # - Identical / near-identical (cosine >= 0.99) -> 99.8% - 100.0%
        # - Verified same identity (cosine >= 0.363) -> 85.0% - 99.5%
        # - Low similarity / non-matches (cosine < 0.363) -> 0.0% - 84.9%
        if cosine_score >= 0.995:
            percentage = 100.0
        elif cosine_score >= 0.363:
            p = 85.0 + ((min(cosine_score, 1.0) - 0.363) / (1.0 - 0.363)) * 14.8
            percentage = round(min(100.0, p), 2)
        else:
            p = max(0.0, (cosine_score + 0.20) / (0.363 + 0.20)) * 84.9
            percentage = round(min(84.9, p), 2)
        
        return cosine_score, percentage

    def rank_candidates(
        self,
        query_embedding: np.ndarray,
        candidate_items: List[Dict[str, Any]],
        threshold: float = 0.60
    ) -> List[Dict[str, Any]]:
        """
        Compares candidate images against the query embedding.
        Each candidate item should be a dict with at least 'image_data' (bytes or ndarray or path).
        Returns list of candidates ranked by similarity score descending.
        """
        ranked = []
        for idx, item in enumerate(candidate_items, start=1):
            img_data = item.get("image_data")
            if img_data is None:
                continue

            try:
                img, face_res, _ = self.detector.detect_primary_face(img_data)
                cand_emb = self.extract_embedding(img, face_res)
                cos_score, pct = self.compute_similarity(query_embedding, cand_emb)
                
                # Check against threshold (threshold can be 0.0-1.0 or 0-100)
                norm_thresh = threshold if threshold <= 1.0 else threshold / 100.0
                is_match = (pct / 100.0) >= norm_thresh

                ranked.append({
                    **item,
                    "candidate_index": idx,
                    "cosine_similarity": cos_score,
                    "similarity_percentage": pct,
                    "is_match": is_match,
                    "face_bbox": face_res.bbox,
                    "face_confidence": face_res.confidence
                })
            except Exception as e:
                logger.debug(f"Candidate {idx} face processing failed: {e}")
                ranked.append({
                    **item,
                    "candidate_index": idx,
                    "error": str(e),
                    "similarity_percentage": 0.0,
                    "is_match": False
                })

        ranked.sort(key=lambda x: x.get("similarity_percentage", 0.0), reverse=True)
        return ranked
