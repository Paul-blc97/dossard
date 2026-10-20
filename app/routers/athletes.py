from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.db import Conn
from app.errors import ApiError
from app.repositories import athletes
from app.schemas import AthleteCreate, AthleteOut, ImportReport

router = APIRouter(prefix="/athletes", tags=["athletes"])


@router.get("", response_model=list[AthleteOut])
def list_athletes(conn: Conn, club: str | None = None) -> list[AthleteOut]:
    return athletes.list_athletes(conn, club=club)


@router.post("/import", response_model=ImportReport)
async def import_athletes(request: Request, conn: Conn) -> ImportReport:
    content_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type != "text/csv":
        raise ApiError("Content-Type attendu : text/csv", code="unsupported_media_type")
    try:
        content = (await request.body()).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ApiError("Le CSV doit être encodé en UTF-8", code="invalid_csv") from exc
    return athletes.import_athletes(conn, content)


@router.get("/{athlete_id}", response_model=AthleteOut)
def get_athlete(athlete_id: int, conn: Conn) -> AthleteOut:
    return athletes.get_athlete(conn, athlete_id)


@router.post("", response_model=AthleteOut, status_code=status.HTTP_201_CREATED)
def create_athlete(data: AthleteCreate, conn: Conn) -> AthleteOut:
    return athletes.create_athlete(conn, data)
