---
name: classement-html
description: Génère une page HTML autonome (un fichier) du classement d'une épreuve de dossard. À utiliser quand on demande une page, un fichier HTML ou une version imprimable/partageable du classement d'une épreuve.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/classement_html.py *)
---

# Classement en HTML

Produit `classement-<event_id>.html` dans le répertoire courant, à partir du classement renvoyé par l'API pour l'épreuve.

## Procédure

1. **Identifier l'épreuve.** Si l'utilisateur donne un identifiant, l'utiliser. Sinon, lister les épreuves depuis la racine du dépôt :
   `sqlite3 data/dossard.db "SELECT id, name, unit FROM events"`
   Si `sqlite3` n'est pas disponible, utiliser `python -c` avec le module `sqlite3` sur `data/dossard.db`. Si plusieurs épreuves correspondent à la demande, demander laquelle.
2. **Lancer le script depuis la racine du dépôt** :
   `python ${CLAUDE_SKILL_DIR}/scripts/classement_html.py <event_id>`
3. **Donner le chemin du fichier produit**, tel qu'affiché par le script (par exemple `/chemin/vers/classement-1.html : 77 athlètes classés`).

## Règles

- Ne jamais écrire ni modifier le HTML à la main : la page doit refléter exactement ce que renvoie l'API.
- Si le script échoue (épreuve introuvable, base absente, classement indisponible), transmettre le message d'erreur tel quel. Ne pas contourner en lisant la base directement pour fabriquer le classement.
- Ne pas modifier `data/dossard.db`.
