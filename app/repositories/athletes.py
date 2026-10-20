from __future__ import annotations

import csv
import io
import sqlite3
from datetime import date, datetime

from pydantic import ValidationError

from app.categories import age_category
from app.errors import ApiError, ConflictError
from app.repositories.common import fetch_or_404
from app.schemas import AthleteCreate, AthleteOut, ImportLineError, ImportReport

IMPORT_COLUMNS = (
    "nom",
    "prenom",
    "date_naissance",
    "sexe",
    "club",
    "licence",
    "certificat_valide_jusqu",
)


def _to_athlete(row: sqlite3.Row) -> AthleteOut:
    birth_date = date.fromisoformat(row["birth_date"])
    certificate = row["medical_certificate_valid_until"]
    return AthleteOut(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        birth_date=birth_date,
        sex=row["sex"],
        club=row["club"],
        license_number=row["license_number"],
        medical_certificate_valid_until=date.fromisoformat(certificate) if certificate else None,
        category=age_category(birth_date),
    )


def list_athletes(
    conn: sqlite3.Connection, club: str | None = None, limit: int = 50, offset: int = 0
) -> list[AthleteOut]:
    sql = "SELECT * FROM athletes"
    params: tuple[str | int, ...] = ()
    if club is not None:
        sql += " WHERE club = ?"
        params = (club,)
    sql += " ORDER BY last_name, first_name, id LIMIT ? OFFSET ?"
    params += (limit, offset)
    return [_to_athlete(row) for row in conn.execute(sql, params)]


def get_athlete(conn: sqlite3.Connection, athlete_id: int) -> AthleteOut:
    row = fetch_or_404(
        conn,
        "SELECT * FROM athletes WHERE id = ?",
        (athlete_id,),
        f"Athlète {athlete_id} introuvable",
    )
    return _to_athlete(row)


def create_athlete(conn: sqlite3.Connection, data: AthleteCreate) -> AthleteOut:
    existing = conn.execute(
        "SELECT id FROM athletes WHERE license_number = ?", (data.license_number,)
    ).fetchone()
    if existing is not None:
        raise ConflictError(f"Licence {data.license_number} déjà enregistrée")

    certificate = data.medical_certificate_valid_until
    cursor = conn.execute(
        "INSERT INTO athletes (first_name, last_name, birth_date, sex, club, license_number,"
        " medical_certificate_valid_until) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data.first_name,
            data.last_name,
            data.birth_date.isoformat(),
            data.sex.value,
            data.club,
            data.license_number,
            certificate.isoformat() if certificate else None,
        ),
    )
    row = conn.execute("SELECT * FROM athletes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_athlete(row)


def _parse_fr_date(value: str) -> date:
    return datetime.strptime(value, "%d/%m/%Y").date()


def _row_to_create(row: dict[str, str]) -> AthleteCreate:
    certificate = (row["certificat_valide_jusqu"] or "").strip()
    return AthleteCreate(
        last_name=(row["nom"] or "").strip(),
        first_name=(row["prenom"] or "").strip(),
        birth_date=_parse_fr_date((row["date_naissance"] or "").strip()),
        sex=(row["sexe"] or "").strip(),
        club=(row["club"] or "").strip() or None,
        license_number=(row["licence"] or "").strip(),
        medical_certificate_valid_until=_parse_fr_date(certificate) if certificate else None,
    )


def import_athletes(conn: sqlite3.Connection, content: str) -> ImportReport:
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    missing = [c for c in IMPORT_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ApiError(f"Colonnes manquantes : {', '.join(missing)}", code="invalid_csv")

    created = 0
    skipped = 0
    errors: list[ImportLineError] = []
    for row in reader:
        line = reader.line_num
        try:
            data = _row_to_create(row)
        except ValidationError as exc:
            detail = "; ".join(f"{'.'.join(map(str, e['loc']))} : {e['msg']}" for e in exc.errors())
            errors.append(ImportLineError(line=line, message=detail))
            continue
        except ValueError as exc:
            errors.append(ImportLineError(line=line, message=f"Date invalide : {exc}"))
            continue

        exists = conn.execute(
            "SELECT 1 FROM athletes WHERE license_number = ?", (data.license_number,)
        ).fetchone()
        if exists is not None:
            skipped += 1
            continue
        create_athlete(conn, data)
        created += 1
    return ImportReport(created=created, skipped=skipped, errors=errors)
