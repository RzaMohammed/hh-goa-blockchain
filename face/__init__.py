"""
Face detection, embedding, and similarity comparison module.
Uses OpenCV deep learning models (YuNet and SFace).
"""
from face.detector import FaceDetector, FaceDetectionResult, FaceError, NoFaceDetectedError, InvalidImageError
from face.matcher import FaceMatcher

__all__ = [
    "FaceDetector",
    "FaceDetectionResult",
    "FaceMatcher",
    "FaceError",
    "NoFaceDetectedError",
    "InvalidImageError"
]
