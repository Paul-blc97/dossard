# Changelog

## Non publié

- Ajoute `GET /competitions/{competition_id}/stats` : nombre d'épreuves, d'inscriptions confirmées et de résultats (inscriptions confirmées seulement) de la compétition ; 404 si la compétition est introuvable.
- `GET /competitions/{competition_id}/results.csv` : les champs contenant une virgule, un guillemet ou un saut de ligne (ex. nom de club) sont désormais entre guillemets, ce qui ne décale plus les colonnes.
- `GET /events/{event_id}/ranking` : la réponse est désormais la liste nue des entrées (plus d'enveloppe `{"data", "count"}`) ; épreuve inconnue → 404 au format d'erreur standard. Routes des résultats : `summary=` en français et fonctions en snake_case.
- `GET /athletes` : pagination `?limit=` (1–100, défaut 50) et `?offset=` (≥ 0, défaut 0) appliquée après le filtre `club` ; valeurs hors bornes rejetées en 422, réponse toujours une liste.
- Ajout de `POST /athletes/import` : import en lot d'un CSV de licenciés (licences existantes ignorées, lignes invalides signalées avec leur numéro). Suppression de `scripts/legacy/import_licencies.py`.
- Ajout de `GET /athletes/{athlete_id}` : détail d'un athlète (404 si introuvable).
