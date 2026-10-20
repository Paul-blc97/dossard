# Changelog

## Non publié

- Ajout de `POST /athletes/import` : import en lot d'un CSV de licenciés (licences existantes ignorées, lignes invalides signalées avec leur numéro). Suppression de `scripts/legacy/import_licencies.py`.
- Ajout de `GET /athletes/{athlete_id}` : détail d'un athlète (404 si introuvable).
