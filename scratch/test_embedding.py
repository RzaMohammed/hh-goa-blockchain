import sys
sys.path.insert(0, '.')
import cv2, numpy as np
from face.detector import FaceDetector
from face.matcher import FaceMatcher

det = FaceDetector()
mat = FaceMatcher(detector=det)

img1, f1, _ = det.detect_primary_face('input/person.jpg')
img2, f2, _ = det.detect_primary_face('input/candidate_same.jpg')
img3, f3, _ = det.detect_primary_face('input/candidate_different.jpg')

def enhanced_extract_embedding(recognizer, img, face_result):
    base_aligned = recognizer.alignCrop(img, face_result.raw_face_data)
    h, w = base_aligned.shape[:2]

    # 1. Base canonical
    f_base = recognizer.feature(base_aligned)
    f_base /= (np.linalg.norm(f_base) + 1e-7)

    # 2. Detail unsharp mask
    try:
        gaussian = cv2.GaussianBlur(base_aligned, (0, 0), 2.0)
        unsharp = cv2.addWeighted(base_aligned, 1.4, gaussian, -0.4, 0)
        f_detail = recognizer.feature(unsharp)
        f_detail /= (np.linalg.norm(f_detail) + 1e-7)
    except Exception:
        f_detail = f_base

    # 3. CLAHE illumination adaptation
    try:
        lab = cv2.cvtColor(base_aligned, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        cl = clahe.apply(l)
        enh = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)
        f_clahe = recognizer.feature(enh)
        f_clahe /= (np.linalg.norm(f_clahe) + 1e-7)
    except Exception:
        f_clahe = f_base

    # 4. Horizontal flip
    f_flip = recognizer.feature(cv2.flip(base_aligned, 1))
    f_flip /= (np.linalg.norm(f_flip) + 1e-7)

    # 5. Tight facial core crop
    try:
        off = max(1, int(h * 0.03))
        tight = cv2.resize(base_aligned[off:h-off, off:w-off], (w, h), interpolation=cv2.INTER_LINEAR)
        f_tight = recognizer.feature(tight)
        f_tight /= (np.linalg.norm(f_tight) + 1e-7)
    except Exception:
        f_tight = f_base

    # Weighted spherical ensemble
    ensemble = 0.40 * f_base + 0.20 * f_detail + 0.15 * f_clahe + 0.15 * f_flip + 0.10 * f_tight
    ensemble /= (np.linalg.norm(ensemble) + 1e-7)
    return ensemble

e1 = enhanced_extract_embedding(mat.recognizer, img1, f1)
e2 = enhanced_extract_embedding(mat.recognizer, img2, f2)
e3 = enhanced_extract_embedding(mat.recognizer, img3, f3)

cos_same, pct_same = mat.compute_similarity(e1, e2)
cos_diff, pct_diff = mat.compute_similarity(e1, e3)

print(f"ENHANCED SAME: cosine={cos_same:.4f}, pct={pct_same:.1f}%")
print(f"ENHANCED DIFF: cosine={cos_diff:.4f}, pct={pct_diff:.1f}%")
