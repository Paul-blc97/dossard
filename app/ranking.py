from __future__ import annotations

import sqlite3

from app.schemas import RankingEntry, ResultUnit


def rank_results(rows: list[sqlite3.Row], unit: ResultUnit) -> list[RankingEntry]:
    """Classe les performances : temps croissants, distances et points décroissants.

    Performances égales : même rang, le suivant saute d'autant de places (1, 2, 2, 4).
    """
    best_first = sorted(rows, key=lambda row: row["performance"], reverse=unit != ResultUnit.TIME_S)
    entries: list[RankingEntry] = []
    for index, row in enumerate(best_first):
        egal_au_precedent = index > 0 and row["performance"] == best_first[index - 1]["performance"]
        entries.append(
            RankingEntry(
                rank=entries[-1].rank if egal_au_precedent else index + 1,
                bib=row["bib"],
                athlete_id=row["athlete_id"],
                last_name=row["last_name"],
                first_name=row["first_name"],
                club=row["club"],
                performance=row["performance"],
            )
        )
    return entries
