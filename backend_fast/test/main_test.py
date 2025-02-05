import pytest
from app.main import filter_accepted_feedbacks

 #Tests the filter feedback function only

def test_filter_accepted_feedbacks():
    feedbacks = [
        {"id": 1, "text": "Improve formatting.", "accepted": True},
        {"id": 2, "text": "Add more details to the experience section.", "accepted": False},
        {"id": 3, "text": "Correct grammatical errors.", "accepted": True},
        {"id": 4, "text": "Update contact information.", "accepted": None},
    ]

    expected_output = [
        {"id": 1, "text": "Improve formatting.", "accepted": True},
        {"id": 3, "text": "Correct grammatical errors.", "accepted": True},
    ]

    assert filter_accepted_feedbacks(feedbacks) == expected_output

def test_filter_accepted_feedbacks_empty():
    feedbacks = []
    assert filter_accepted_feedbacks(feedbacks) == []

def test_filter_accepted_feedbacks_no_accepted():
    feedbacks = [
        {"id": 1, "text": "Add references.", "accepted": False},
        {"id": 2, "text": "Include certifications.", "accepted": None},
    ]
    assert filter_accepted_feedbacks(feedbacks) == []

