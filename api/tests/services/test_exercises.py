"""Exercise library service: idempotent seed + filtered keyset listing."""
from __future__ import annotations

from app.services.exercises import list_exercises, upsert_exercises


def make_raw(
    id_: str,
    name: str,
    *,
    body_part: str = "waist",
    target: str = "abs",
    equipment: str = "body weight",
) -> dict:
    """A record shaped like one entry of data/exercises.json."""
    return {
        "id": id_,
        "name": name,
        "category": body_part,
        "body_part": body_part,
        "equipment": equipment,
        "instructions": {"en": "Do the movement with control."},
        "instruction_steps": {"en": ["Set up.", "Do the movement with control."]},
        "muscle_group": "hip flexors",
        "secondary_muscles": ["hip flexors", "lower back"],
        "target": target,
        "image": f"images/{id_}-abc.jpg",
        "gif_url": f"videos/{id_}-abc.gif",
        "media_id": "abc",
        "created_at": "2026-03-18T12:31:32+00:00",
        "attribution": "Gym visual - https://gymvisual.com/",
    }


RAW = [
    make_raw("0001", "3/4 sit-up"),
    make_raw("0002", "45 degree side bend", target="obliques"),
    make_raw(
        "0003",
        "barbell bench press",
        body_part="chest",
        target="pectorals",
        equipment="barbell",
    ),
]


def test_upsert_is_idempotent_and_updates(db_session):
    assert upsert_exercises(db_session, RAW) == 3
    renamed = [dict(RAW[0], name="3/4 sit-up (renamed)"), *RAW[1:]]
    assert upsert_exercises(db_session, renamed) == 3

    page = list_exercises(db_session)
    assert len(page["items"]) == 3
    names = {e["name"] for e in page["items"]}
    assert "3/4 sit-up (renamed)" in names and "3/4 sit-up" not in names


def test_media_urls_are_absolute_cdn(db_session):
    upsert_exercises(db_session, RAW)
    item = next(
        e for e in list_exercises(db_session)["items"] if e["id"] == "0001"
    )
    assert item["gif_url"].startswith("https://")
    assert item["gif_url"].endswith("videos/0001-abc.gif")
    assert item["image_url"].startswith("https://")
    assert item["image_url"].endswith("images/0001-abc.jpg")


def test_filters_and_search(db_session):
    upsert_exercises(db_session, RAW)

    chest = list_exercises(db_session, body_part="chest")["items"]
    assert [e["id"] for e in chest] == ["0003"]

    barbell = list_exercises(db_session, equipment="barbell")["items"]
    assert [e["id"] for e in barbell] == ["0003"]

    found = list_exercises(db_session, q="BENCH")["items"]
    assert [e["id"] for e in found] == ["0003"]

    assert list_exercises(db_session, q="deadlift")["items"] == []


def test_keyset_pagination_walks_all_without_duplicates(db_session):
    upsert_exercises(db_session, RAW)

    seen: list[str] = []
    cursor = None
    for _ in range(5):
        page = list_exercises(db_session, limit=2, cursor=cursor)
        seen += [e["id"] for e in page["items"]]
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert sorted(seen) == ["0001", "0002", "0003"]
    assert len(seen) == len(set(seen))
