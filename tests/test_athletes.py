from datetime import date
from pathlib import Path


def test_create_athlete_returns_201_with_category(client):
    birth_date = date(date.today().year - 30, 3, 2)

    response = client.post(
        "/athletes",
        json={
            "first_name": "Inès",
            "last_name": "Morel",
            "birth_date": birth_date.isoformat(),
            "sex": "F",
            "license_number": "DOS-000042",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["category"] == "SENIOR"
    assert body["club"] is None


def test_create_athlete_rejects_duplicate_license(client, make_athlete):
    athlete = make_athlete()

    response = client.post(
        "/athletes",
        json={
            "first_name": "Hugo",
            "last_name": "Lemaire",
            "birth_date": "1995-05-20",
            "sex": "M",
            "license_number": athlete["license_number"],
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_list_athletes_filters_by_club(client, make_athlete):
    make_athlete("Durand", club="AC Rivebelle")
    make_athlete("Petit", club="Stade Nordval")

    response = client.get("/athletes", params={"club": "AC Rivebelle"})

    assert response.status_code == 200
    assert [a["last_name"] for a in response.json()] == ["Durand"]


def test_get_athlete_returns_detail(client, make_athlete):
    athlete = make_athlete("Durand")

    response = client.get(f"/athletes/{athlete['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == athlete["id"]
    assert body["last_name"] == "Durand"
    assert "category" in body


def test_get_athlete_unknown_returns_404(client):
    response = client.get("/athletes/9999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_get_athlete_invalid_id_returns_422(client):
    response = client.get("/athletes/abc")

    assert response.status_code == 422


CSV_EXEMPLE = Path(__file__).parent.parent / "scripts" / "legacy" / "licencies_exemple.csv"


def _import_csv(client, content: bytes):
    return client.post("/athletes/import", content=content, headers={"Content-Type": "text/csv"})


def test_import_licencies_exemple(client):
    response = _import_csv(client, CSV_EXEMPLE.read_bytes())

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 17
    assert body["skipped"] == 1
    assert [e["line"] for e in body["errors"]] == [15, 16]
    assert len(client.get("/athletes").json()) == 17


def test_import_licencies_reimport(client):
    content = CSV_EXEMPLE.read_bytes()
    first = _import_csv(client, content).json()

    body = _import_csv(client, content).json()

    assert body["created"] == 0
    assert body["skipped"] == 18
    assert body["errors"] == first["errors"]
    assert len(client.get("/athletes").json()) == 17


def test_import_rejects_wrong_content_type(client):
    response = client.post("/athletes/import", content=b"x", headers={"Content-Type": "text/plain"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_media_type"


def test_import_rejects_missing_columns(client):
    response = _import_csv(client, b"nom;prenom\nDurand;Luc\n")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_csv"
