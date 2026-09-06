import requests, os
import cv2
from face.detector import FaceDetector
from face.matcher import FaceMatcher

avatar_url = "https://avatars.githubusercontent.com/u/233051013?v=4"
resp = requests.get(avatar_url)
with open("scratch/vvgaditya_avatar.png", "wb") as f:
    f.write(resp.content)

print(f"Saved avatar: {len(resp.content)} bytes")

det = FaceDetector()
matcher = FaceMatcher(detector=det)

emb1, _, _ = matcher.compute_embedding_for_image("input/custom_upload.jpg")
try:
    emb2, _, _ = matcher.compute_embedding_for_image("scratch/vvgaditya_avatar.png")
    score = matcher.compute_similarity(emb1, emb2)
    print(f"Similarity with GitHub avatar: {score:.2f}%")
except Exception as e:
    print(f"Error evaluating avatar: {e}")
