"""
Unit tests for the improved face-search and best-match system.
Validates:
1. Multi-face candidate evaluation (extracting embeddings for each face in an image).
2. Strict biometric similarity ranking independent of search engine order.
3. Configurable threshold enforcement ('No high-confidence match found').
4. Ambiguity detection when top two candidates have very close similarity scores.
5. Top 5 candidate preservation for debugging and inspection.
"""
import os
import pytest
import numpy as np

from face.detector import FaceDetector
from face.matcher import FaceMatcher, RankedCandidateList


@pytest.fixture(scope="module")
def detector_and_matcher():
    det = FaceDetector()
    matcher = FaceMatcher(detector=det)
    return det, matcher


def test_multi_face_candidate_evaluation(detector_and_matcher):
    det, matcher = detector_and_matcher
    query_img = "input/person.jpg"
    group_img = "input/candidate_group.jpg"

    assert os.path.exists(query_img), "input/person.jpg must exist"
    assert os.path.exists(group_img), "input/candidate_group.jpg must exist"

    # Verify that candidate_group contains multiple faces
    _, faces = det.detect_all_faces(group_img)
    assert len(faces) >= 2, f"Expected at least 2 faces in group image, found {len(faces)}"

    query_embedding, _, _ = matcher.compute_embedding_for_image(query_img)

    # Candidate with multiple faces
    candidates = [{
        "title": "Group Photo Candidate",
        "source_url": "https://example.com/group",
        "image_data": group_img
    }]

    ranked = matcher.rank_candidates(query_embedding, candidates, threshold=0.55)

    assert len(ranked) == 1
    cand_res = ranked[0]
    # Faces count should be detected accurately
    assert cand_res["faces_detected_count"] >= 2
    # All faces in the image should have been evaluated
    assert len(cand_res["evaluated_faces"]) >= 2
    # Highest match in the group (matching person) should be selected (>= 98.0%)
    assert cand_res["similarity_percentage"] >= 98.0
    assert cand_res["is_match"] is True


def test_strict_similarity_ranking_independent_of_order(detector_and_matcher):
    det, matcher = detector_and_matcher
    query_img = "input/person.jpg"
    same_img = "input/candidate_same.jpg"
    diff_img = "input/candidate_different.jpg"

    query_embedding, _, _ = matcher.compute_embedding_for_image(query_img)

    # Put the non-matching candidate FIRST, and matching candidate SECOND
    candidates = [
        {"title": "Search Engine Top Result (Non-Match)", "image_data": diff_img},
        {"title": "Search Engine Buried Result (Genuine Match)", "image_data": same_img}
    ]

    ranked = matcher.rank_candidates(query_embedding, candidates, threshold=0.55)

    # The face recognition system must decide the best match, NOT search order
    assert ranked[0]["title"] == "Search Engine Buried Result (Genuine Match)"
    assert ranked[0]["similarity_percentage"] > ranked[1]["similarity_percentage"]
    assert ranked[0]["similarity_percentage"] >= 98.0
    assert ranked[1]["similarity_percentage"] < 45.0


def test_threshold_enforcement_no_match(detector_and_matcher):
    det, matcher = detector_and_matcher
    query_img = "input/candidate_different.jpg"
    diff_img = "input/person.jpg"

    query_embedding, _, _ = matcher.compute_embedding_for_image(query_img)

    candidates = [
        {"title": "Non-matching candidate", "image_data": diff_img}
    ]

    # Set threshold to 55%
    ranked = matcher.rank_candidates(query_embedding, candidates, threshold=0.55)
    best = ranked[0]

    # The score should be ~25.6%, which is below the 55% threshold
    assert best["similarity_percentage"] < 55.0
    assert best["is_match"] is False


def test_ambiguity_detection_top_two(detector_and_matcher):
    det, matcher = detector_and_matcher
    query_img = "input/person.jpg"
    same_img1 = "input/candidate_same.jpg"
    same_img2 = "input/candidate_group.jpg"

    query_embedding, _, _ = matcher.compute_embedding_for_image(query_img)

    # Both images contain the matching face and have very close scores (>= 98.0% and diff < 3.0%)
    candidates = [
        {"title": "Profile A (Flickr)", "image_data": same_img1},
        {"title": "Profile B (Group)", "image_data": same_img2}
    ]

    ranked = matcher.rank_candidates(query_embedding, candidates, threshold=0.55, ambiguity_delta=3.0)

    assert ranked.is_ambiguous is True
    assert ranked.ambiguity_details is not None
    assert ranked.ambiguity_details["delta"] <= 3.0
    assert ranked.ambiguity_details["top1_score"] >= 98.0
    assert ranked.ambiguity_details["top2_score"] >= 98.0


def test_top_5_candidates_retained(detector_and_matcher):
    det, matcher = detector_and_matcher
    query_img = "input/person.jpg"
    query_embedding, _, _ = matcher.compute_embedding_for_image(query_img)

    # Create 7 candidate items
    candidates = [
        {"title": f"Candidate #{i}", "image_data": "input/candidate_different.jpg"}
        for i in range(7)
    ]
    # Make candidate #4 the genuine match
    candidates[4]["image_data"] = "input/candidate_same.jpg"
    candidates[4]["title"] = "Candidate #4 (Genuine Match)"

    ranked = matcher.rank_candidates(query_embedding, candidates, threshold=0.55)

    assert len(ranked) == 7
    assert len(ranked.top_5) == 5
    # The genuine match must be ranked #1
    assert ranked.top_5[0]["title"] == "Candidate #4 (Genuine Match)"
    assert ranked[0]["similarity_percentage"] >= 98.0
