#!/usr/bin/env python3
"""Hook PreToolUse : bloque les commandes destructrices dans les outils shell.

Lit le JSON envoyé par Claude Code sur l'entrée standard. Si la commande
Bash ou PowerShell contient rm -rf, git push --force (ou -f) ou DROP TABLE /
DROP VIEW, écrit un message sur la sortie d'erreur et sort avec le code 2
(blocage). Sinon, sort avec le code 0.
"""

import json
import re
import sys

OUTILS_SURVEILLES = {"Bash", "PowerShell"}

# Options de rm : au moins une forme courte ou longue de « récursif » et « forcé ».
RE_RM = re.compile(r"\brm\b((?:\s+-{1,2}[A-Za-z][A-Za-z-]*)+)")
RE_GIT_PUSH = re.compile(r"\bgit\s+push\b([^;&|\n]*)")
RE_DROP = re.compile(r"\bDROP\s+(?:TABLE|VIEW)\b", re.IGNORECASE)


def raison_blocage(commande: str) -> str | None:
    """Renvoie la raison du blocage, ou None si la commande est autorisée."""
    for match in RE_RM.finditer(commande):
        options = match.group(1).split()
        courtes = "".join(o[1:] for o in options if not o.startswith("--"))
        longues = {o for o in options if o.startswith("--")}
        if ("r" in courtes or "R" in courtes or "--recursive" in longues) and (
            "f" in courtes or "--force" in longues
        ):
            return "rm -rf (suppression récursive forcée)"

    for match in RE_GIT_PUSH.finditer(commande):
        arguments = match.group(1).split()
        if "--force" in arguments or "-f" in arguments:
            return "git push --force (réécriture de l'historique distant)"

    if RE_DROP.search(commande):
        return "DROP TABLE / DROP VIEW (suppression de schéma)"

    return None


def main() -> int:
    """Point d'entrée : lit l'événement et décide du blocage."""
    try:
        evenement = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if evenement.get("tool_name") not in OUTILS_SURVEILLES:
        return 0

    commande = (evenement.get("tool_input") or {}).get("command")
    if not isinstance(commande, str):
        return 0

    raison = raison_blocage(commande)
    if raison is None:
        return 0

    print(f"Bloqué par le hook garde.py : {raison}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
