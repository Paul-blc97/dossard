# CLAUDE.md

Dossard : API de gestion de compétitions sportives (FastAPI + SQLite + pytest), projet fil rouge d'une formation Claude Code. Le code, les commentaires, les docstrings et les messages d'erreur sont en français : suivre cette langue.

## Commandes

```bash
pip install -e ".[dev]"             # dans un venv, Python >= 3.12
pytest                              # tous les tests (doivent être verts avant tout commit)
pytest tests/test_results.py::test_nom   # un seul test
ruff check . && ruff format .       # lint + formatage (ligne 100, règle ANN : annotations obligatoires hors tests)
python scripts/seed.py [--reset]    # données synthétiques dans data/dossard.db
uvicorn app.main:app --reload       # http://localhost:8000, doc sur /docs
```

## Architecture

Trois couches, un module par entité (competitions, athletes, registrations, results) :
`app/routers/*` (endpoints fins) → `app/repositories/*` (SQL brut via `sqlite3`, pas d'ORM) → `app/schema.sql`. Modèles Pydantic et énumérations dans `app/schemas.py`. Logique pure séparée : `app/categories.py` (catégorie d'âge = année de saison − année de naissance), `app/ranking.py` (temps croissants, distances/points décroissants).

- **Connexion** : `Conn` (`app/db.py`) est une dépendance FastAPI, une connexion par requête, commit en fin de requête, rollback sur exception. Les repositories reçoivent `conn` et ne committent pas. Chemin de la base : variable `DOSSARD_DB`, sinon `data/dossard.db`. Le schéma est créé de façon idempotente au démarrage (`init_db`, `CREATE ... IF NOT EXISTS` : pas de migrations).
- **Erreurs** : lever `NotFoundError` / `ConflictError` / `ApiError(message, code=...)` (`app/errors.py`) ; le handler global de `app/main.py` les sérialise en `{"error": {"code", "message"}}`. Utiliser `fetch_or_404` (`app/repositories/common.py`) pour « une ligne ou 404 ».
- **Règles métier** : statuts de compétition en chaîne `draft → open → closed → finished` (`invalid_transition`), inscriptions seulement si compétition ouverte (`registrations_closed`), catégorie de l'athlète = celle de l'épreuve (`category_mismatch`).
- **Vues publiques** : `v_public_athletes` et `v_public_results` dans `schema.sql` n'exposent que des colonnes non sensibles (année de naissance, pas de licence ni de certificat médical ; seulement les inscriptions confirmées). Le serveur MCP ne lit que ces vues : ne pas les élargir sans raison.

## Tests

`tests/conftest.py` : chaque test a sa propre base temporaire (jamais `data/dossard.db`) via `DOSSARD_DB`.

- Réutiliser les fixtures `client`, `make_competition`, `make_event`, `make_athlete`, `make_registration` (créer les données via l'API, pas en base).
- Un fichier de test par router.
- Toujours tester les cas d'erreur : 404, 409, 422.

## Règles du projet

- Après toute modification Python : `ruff check . && ruff format .` (obligatoire).
- Erreurs : toujours passer par `app/errors.py` (`ApiError`, `NotFoundError`, `ConflictError`), jamais `HTTPException`. Format de sortie : `{"error": {"code", "message"}}`.
- Toute route ajoutée ou modifiée : une ligne dans `docs/api.md` et une entrée en tête de `CHANGELOG.md`, section « Non publié » (créer le fichier s'il n'existe pas).
- `scripts/legacy/` : lecture autorisée, aucune modification ni suppression sans demande explicite (exclu de ruff).
- Pas de nouvelle dépendance sans demander.
- Scripts annexes autonomes : `scripts/classement_html.py <event_id>` (page HTML via l'API en interne), `scripts/mcp_dossard.py` (serveur MCP stdio, stdlib seule, base en lecture seule `mode=ro`, vues publiques uniquement, pas de SQL libre), `scripts/recepteur_hooks.py` (récepteur local de hooks HTTP).
- Les données d'exemple et de test sont synthétiques : aucune donnée personnelle réelle.
- `CLAUDE.local.md` et `.claude/settings.local.json` sont personnels et ignorés par Git.
- Ne jamais lire ni afficher .env : il contient des secrets.

## Écrire dans ce fichier

- Une instruction = une ligne vérifiable (« lancer `pytest` » plutôt que « tester correctement »).
- Des commandes exactes, pas des intentions.
- Rien que Claude pourrait lire dans le code en 10 secondes.
