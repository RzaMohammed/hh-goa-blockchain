"""
Tests for face detection and matching modules.
"""
import pytest
import numpy as np
import cv2
from face.detector import FaceDetector, NoFaceDetectedError, InvalidImageError
from face.matcher import FaceMatcher


def test_invalid_image_raises_error():
    detector = FaceDetector()
    with pytest.raises(InvalidImageError):
        detector.detect_all_faces("non_existent_file.jpg")


def test_no_face_detected_raises_error():
    detector = FaceDetector()
    # Create blank black image
    blank_img = np.zeros((300, 300, 3), dtype=np.uint8)
    with pytest.raises(NoFaceDetectedError):
        detector.detect_primary_face(blank_img)


def test_detector_detect_all_faces_on_blank():
    detector = FaceDetector()
    blank_img = np.zeros((300, 300, 3), dtype=np.uint8)
    img, faces = detector.detect_all_faces(blank_img)
    assert len(faces) == 0
    assert img.shape == (300, 300, 3)


def test_matcher_self_similarity():
    # If we have a dummy embedding, matching it with itself should be 100% or very close
    matcher = FaceMatcher()
    dummy_feat = np.random.randn(1, 128).astype(np.float32)
    # L2 normalize
    dummy_feat = dummy_feat / np.linalg.norm(dummy_feat)
    cos_score, pct = matcher.compute_similarity(dummy_feat, dummy_feat)
    # Cosine score of identical normalized vector is 1.0
    assert cos_score >= 0.99
    assert pct >= 99.0
