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
    def __init__(self, model_path: Optional[str] = None, conf_threshold: float = 0.45, nms_threshold: float = 0.3):
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
        # Load Haar Cascade as a secondary safety net
        try:
            haar_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
            self.haar_cascade = cv2.CascadeClassifier(haar_path)
        except Exception:
            self.haar_cascade = None

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
                try:
                    import io
                    from PIL import Image
                    pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
                    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                except Exception:
                    pass
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
        Detects all faces in the provided image using multi-pass YuNet and Haar fallback.
        Returns (img_bgr, list_of_FaceDetectionResult).
        """
        img = self.load_image(image_input)
        h, w = img.shape[:2]
        self.detector.setInputSize((w, h))

        # Pass 1: Standard YuNet detection
        _, faces = self.detector.detect(img)

        # Pass 2: Adaptive CLAHE enhancement for dim or backlit frames
        if faces is None or len(faces) == 0:
            try:
                lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                cl = clahe.apply(l)
                enhanced = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)
                _, faces = self.detector.detect(enhanced)
            except Exception:
                pass

        # Pass 3: Multi-scale resizing for distant webcam portraits or ultra-high-res images
        if (faces is None or len(faces) == 0) and (w > 800 or w < 320):
            try:
                scale = 640.0 / w
                target_w = 640
                target_h = int(h * scale)
                scaled = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)
                self.detector.setInputSize((target_w, target_h))
                _, scaled_faces = self.detector.detect(scaled)
                self.detector.setInputSize((w, h))  # Reset size
                if scaled_faces is not None and len(scaled_faces) > 0:
                    # Rescale bounding boxes and landmarks back to original dimensions
                    faces = []
                    inv_scale = 1.0 / scale
                    for sf in scaled_faces:
                        orig_f = sf.copy()
                        orig_f[0:4] = sf[0:4] * inv_scale
                        orig_f[4:14] = sf[4:14] * inv_scale
                        faces.append(orig_f)
                    faces = np.array(faces)
            except Exception:
                pass

        # Pass 4: Multi-scale high-res pyramid pass for small or distant faces
        if (faces is None or len(faces) == 0) and (w > 300 and h > 300):
            try:
                # Try 1.25x upscaled detection for small faces in web portraits
                up_w = min(1200, int(w * 1.25))
                up_h = min(1200, int(h * 1.25))
                scaled_up = cv2.resize(img, (up_w, up_h), interpolation=cv2.INTER_LINEAR)
                self.detector.setInputSize((up_w, up_h))
                _, up_faces = self.detector.detect(scaled_up)
                self.detector.setInputSize((w, h))  # Reset size
                if up_faces is not None and len(up_faces) > 0:
                    faces = []
                    scale_x = w / float(up_w)
                    scale_y = h / float(up_h)
                    for uf in up_faces:
                        orig_f = uf.copy()
                        orig_f[0] *= scale_x
                        orig_f[1] *= scale_y
                        orig_f[2] *= scale_x
                        orig_f[3] *= scale_y
                        for l_i in range(4, 14, 2):
                            orig_f[l_i] *= scale_x
                            orig_f[l_i + 1] *= scale_y
                        faces.append(orig_f)
                    faces = np.array(faces)
            except Exception:
                pass

        if faces is None or len(faces) == 0:
            return img, []

        results = []
        for face in faces:
            x, y, fw, fh = map(int, face[0:4])
            score = float(face[14])
            
            # 1. Size & confidence gate for real human faces
            if fw < 20 or fh < 20 or score < 0.40:
                continue

            # 2. Aspect ratio check (human faces typically have w/h between 0.55 and 1.45)
            aspect = fw / float(fh) if fh > 0 else 0
            if aspect < 0.50 or aspect > 1.60:
                continue

            # 3. Biometric Landmark Sanity Check:
            # YuNet outputs: right_eye(x,y), left_eye(x,y), nose(x,y), right_mouth(x,y), left_mouth(x,y)
            landmarks = face[4:14].reshape((5, 2))
            re_x, re_y = landmarks[0]
            le_x, le_y = landmarks[1]
            nt_x, nt_y = landmarks[2]
            rm_x, rm_y = landmarks[3]
            lm_x, lm_y = landmarks[4]

            # Eye distance check
            eye_dist = np.hypot(le_x - re_x, le_y - re_y)
            if eye_dist < 8.0:
                continue

            # Nose must be vertically between eyes and mouth
            eye_avg_y = (re_y + le_y) / 2.0
            mouth_avg_y = (rm_y + lm_y) / 2.0
            if not (eye_avg_y <= nt_y <= mouth_avg_y + 10.0):
                continue

            # Mouth must be lower than eyes
            if mouth_avg_y <= eye_avg_y:
                continue

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
        Selects the most prominent face using bounding box area and proximity to frame center.
        Returns (img_bgr, primary_face_result, total_face_count).
        Raises NoFaceDetectedError if 0 faces found.
        """
        img, faces = self.detect_all_faces(image_input)
        face_count = len(faces)

        if face_count == 0:
            raise NoFaceDetectedError("No face detected in the provided image.")

        if face_count > 1:
            h, w = img.shape[:2]
            cx, cy = w / 2.0, h / 2.0
            max_dist = np.hypot(cx, cy)

            def face_prominence(f: FaceDetectionResult) -> float:
                fx, fy, fw, fh = f.bbox
                area = fw * fh
                fcx = fx + fw / 2.0
                fcy = fy + fh / 2.0
                dist = np.hypot(fcx - cx, fcy - cy)
                center_bonus = 1.0 - 0.35 * (dist / max_dist) if max_dist > 0 else 1.0
                return area * center_bonus * f.confidence

            faces.sort(key=face_prominence, reverse=True)

        return img, faces[0], face_count
