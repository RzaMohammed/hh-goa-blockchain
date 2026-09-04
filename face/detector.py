"""
Face detector implementation using OpenCV YuNet (Deep Learning Model).
Detects faces and facial landmarks with high speed and accuracy.
"""
import os
import urllib.request
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple
import cv2
import numpy as np

logger = logging.getLogger(__name__)

YUNET_MODEL_URL = "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx"
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
DEFAULT_YUNET_PATH = os.path.join(DEFAULT_MODEL_DIR, "face_detection_yunet_2023mar.onnx")


class FaceError(Exception):
    """Base exception for face processing errors."""
    pass


class InvalidImageError(FaceError):
    """Raised when an image cannot be read or is invalid."""
    pass


class NoFaceDetectedError(FaceError):
    """Raised when no face is detected in the input image."""
    pass


@dataclass
class FaceDetectionResult:
    """Represents a detected face with bounding box, score, and landmarks."""
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    confidence: float
    landmarks: np.ndarray            # 5 landmarks (right eye, left eye, nose, mouth right, mouth left)
    raw_face_data: np.ndarray        # 15-element array as returned by YuNet


def ensure_model_exists(model_path: str, download_url: str) -> str:
    """Ensures model file exists, downloading it if necessary."""
    if not os.path.exists(model_path) or os.path.getsize(model_path) < 10000:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        logger.info(f"Downloading model to {model_path}...")
        urllib.request.urlretrieve(download_url, model_path)
    return model_path


class FaceDetector:
    """
    Detects faces in images using OpenCV DNN YuNet.
    """
    def __init__(self, model_path: Optional[str] = None, conf_threshold: float = 0.6, nms_threshold: float = 0.3):
        self.model_path = model_path or DEFAULT_YUNET_PATH
        ensure_model_exists(self.model_path, YUNET_MODEL_URL)
        
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.detector = cv2.FaceDetectorYN.create(
            model=self.model_path,
            config="",
            input_size=(320, 320),
            score_threshold=self.conf_threshold,
            nms_threshold=self.nms_threshold,
            top_k=5000
        )

    def load_image(self, image_input) -> np.ndarray:
        """
        Loads an image from file path, byte buffer, or validates numpy array.
        Returns BGR image array.
        """
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise InvalidImageError(f"Image file does not exist: {image_input}")
            img = cv2.imread(image_input)
            if img is None:
                raise InvalidImageError(f"Failed to read image file (corrupted or unsupported format): {image_input}")
            return img
        elif isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise InvalidImageError("Failed to decode image bytes.")
            return img
        elif isinstance(image_input, np.ndarray):
            if image_input.size == 0:
                raise InvalidImageError("Provided numpy array image is empty.")
            if len(image_input.shape) == 2:
                return cv2.cvtColor(image_input, cv2.COLOR_GRAY2BGR)
            elif len(image_input.shape) == 3 and image_input.shape[2] == 4:
                return cv2.cvtColor(image_input, cv2.COLOR_BGRA2BGR)
            return image_input
        else:
            raise InvalidImageError(f"Unsupported image input type: {type(image_input)}")

    def detect_all_faces(self, image_input) -> Tuple[np.ndarray, List[FaceDetectionResult]]:
        """
        Detects all faces in the provided image.
        Returns (img_bgr, list_of_FaceDetectionResult).
        """
        img = self.load_image(image_input)
        h, w = img.shape[:2]
        self.detector.setInputSize((w, h))

        _, faces = self.detector.detect(img)
        if faces is None or len(faces) == 0:
            return img, []

        results = []
        for face in faces:
            x, y, fw, fh = map(int, face[0:4])
            score = float(face[14])
            landmarks = face[4:14].reshape((5, 2))
            results.append(FaceDetectionResult(
                bbox=(x, y, fw, fh),
                confidence=score,
                landmarks=landmarks,
                raw_face_data=face
            ))

        return img, results

    def detect_primary_face(self, image_input) -> Tuple[np.ndarray, FaceDetectionResult, int]:
        """
        Detects the primary face in the image.
        If multiple faces are detected, selects the one with the largest bounding box area.
        Returns (img_bgr, primary_face_result, total_face_count).
        Raises NoFaceDetectedError if 0 faces found.
        """
        img, faces = self.detect_all_faces(image_input)
        face_count = len(faces)

        if face_count == 0:
            raise NoFaceDetectedError("No face detected in the provided image.")

        if face_count > 1:
            logger.warning(f"Multiple faces ({face_count}) detected in the image. Selecting primary face by area.")
            # Sort by area (w * h) descending
            faces.sort(key=lambda f: f.bbox[2] * f.bbox[3], reverse=True)

        return img, faces[0], face_count
