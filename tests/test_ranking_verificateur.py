import pytest


@pytest.fixture
def classement(client, make_competition, make_event, make_athlete, make_registration):
    """Fabrique : épreuve close avec un résultat par performance, renvoie le classement."""

    def _make(unit: str, performances: list[float]) -> list[dict]:
        competition = make_competition(status="open")
        event = make_event(competition["id"], unit=unit)
        registrations = [
            make_registration(event["id"], make_athlete(f"Athlete{i}")["id"])
            for i in range(len(performances))
        ]
        client.patch(f"/competitions/{competition['id']}", json={"status": "closed"})
        for registration, performance in zip(registrations, performances, strict=True):
            response = client.put(
                f"/registrations/{registration['id']}/result", json={"performance": performance}
            )
            assert response.status_code == 200
        response = client.get(f"/events/{event['id']}/ranking")
        assert response.status_code == 200
        return response.json()

    return _make


def _rangs(classement):
    return [e["rank"] for e in classement]


def test_ex_aequo_au_milieu_saute_un_rang(classement):
    assert _rangs(classement("time_s", [10.0, 11.0, 11.0, 12.0])) == [1, 2, 2, 4]


def test_ex_aequo_en_tete(classement):
    assert _rangs(classement("time_s", [10.0, 10.0, 11.0])) == [1, 1, 3]


def test_ex_aequo_en_queue(classement):
    assert _rangs(classement("time_s", [10.0, 11.0, 11.0])) == [1, 2, 2]


def test_triple_ex_aequo_saute_deux_rangs(classement):
    assert _rangs(classement("time_s", [10.0, 11.0, 11.0, 11.0, 12.0])) == [1, 2, 2, 2, 5]


def test_deux_groupes_d_ex_aequo(classement):
    assert _rangs(classement("time_s", [10.0, 10.0, 11.0, 11.0, 12.0])) == [1, 1, 3, 3, 5]


def test_tous_ex_aequo(classement):
    assert _rangs(classement("time_s", [10.0, 10.0, 10.0])) == [1, 1, 1]


def test_sans_ex_aequo_rangs_consecutifs(classement):
    assert _rangs(classement("time_s", [12.0, 10.0, 11.0])) == [1, 2, 3]


def test_un_seul_resultat(classement):
    assert _rangs(classement("time_s", [10.0])) == [1]


def test_classement_vide(classement):
    assert classement("time_s", []) == []


def test_ex_aequo_distances_ordre_decroissant(classement):
    ranking = classement("distance_m", [6.0, 6.5, 6.5, 7.0])
    assert [(e["rank"], e["performance"]) for e in ranking] == [
        (1, 7.0),
        (2, 6.5),
        (2, 6.5),
        (4, 6.0),
    ]


def test_ex_aequo_points_ordre_decroissant(classement):
    ranking = classement("points", [800, 900, 900, 700])
    assert _rangs(ranking) == [1, 1, 3, 4]


def test_classement_epreuve_inconnue_404(client):
    response = client.get("/events/999/ranking")

    assert response.status_code == 404
    assert response.json()["error"]["code"]
