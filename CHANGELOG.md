# Changelog

## Non publié

- `GET /athletes` : pagination `?limit=` (1–100, défaut 50) et `?offset=` (≥ 0, défaut 0) appliquée après le filtre `club` ; valeurs hors bornes rejetées en 422, réponse toujours une liste.
- Ajout de `POST /athletes/import` : import en lot d'un CSV de licenciés (licences existantes ignorées, lignes invalides signalées avec leur numéro). Suppression de `scripts/legacy/import_licencies.py`.
- Ajout de `GET /athletes/{athlete_id}` : détail d'un athlète (404 si introuvable).
