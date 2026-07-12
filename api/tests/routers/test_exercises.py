"""GET /exercises endpoints (library is available to every signed-in user)."""
from __future__ import annotations

from app.services.exercises import upsert_exercises

from tests.services.test_exercises import RAW


def test_list_exercises_with_filter(app_client, db_session):
    upsert_exercises(db_session, RAW)

    res = app_client.get("/exercises", params={"body_part": "chest"})
    assert res.status_code == 200
    body = res.json()
    assert [e["id"] for e in body["items"]] == ["0003"]
    assert body["next_cursor"] is None


def test_exercise_detail_includes_instructions(app_client, db_session):
    upsert_exercises(db_session, RAW)

    res = app_client.get("/exercises/0001")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "3/4 sit-up"
    assert body["instructions"] == ["Set up.", "Do the movement with control."]
    assert body["secondary_muscles"] == ["hip flexors", "lower back"]
    assert body["attribution"]


def test_exercise_detail_unknown_is_404(app_client, db_session):
    res = app_client.get("/exercises/9999")
    assert res.status_code == 404
    assert res.json()["error"]["message"] == "exercise_not_found"


def test_list_requires_auth(client):
    assert client.get("/exercises").status_code == 401
