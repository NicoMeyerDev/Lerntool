"""PreToolUse-Hook: blockiert gefährliche Git-Befehle.

Exit-Code 2 blockiert den Befehl, die Meldung geht an Claude.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

GESCHUETZTE_BRANCHES = {"main", "master"}


def aktueller_branch() -> str:
    """Gibt den Namen des aktuellen Git-Branches zurück (leer bei Fehler)."""
    try:
        ergebnis = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=10,
        )
        return ergebnis.stdout.strip()
    except Exception:
        return ""


def pruefe(befehl: str) -> str | None:
    """Prüft einen Shell-Befehl und liefert eine Verbotsmeldung oder None.

    Args:
        befehl: Der Bash-Befehl, den Claude ausführen will.
    """
    if not re.search(r"\bgit\b", befehl):
        return None

    branch = aktueller_branch()

    if "--no-verify" in befehl:
        return "Verboten: --no-verify umgeht die Prüfungen."
    if re.search(r"\bgit\b.*\breset\b.*--hard", befehl):
        return "Verboten: git reset --hard."
    if re.search(r"\bgit\b.*\bpush\b", befehl):
        if re.search(r"--force|--force-with-lease|\s-f\b", befehl):
            return "Verboten: Force-Push."
        if re.search(r"\b(main|master)\b", befehl):
            return "Verboten: Push auf main. Nutze einen Feature-Branch und einen Pull Request."
        if branch in GESCHUETZTE_BRANCHES:
            return "Verboten: Push, solange du auf main bist. Wechsle auf einen Feature-Branch."
    if re.search(r"\bgit\b.*\bcommit\b", befehl) and branch in GESCHUETZTE_BRANCHES:
        return "Verboten: Commit auf main. Lege zuerst einen Feature-Branch an."
    return None


def main() -> None:
    """Liest den Hook-Aufruf von stdin und blockiert verbotene Befehle."""
    daten = json.load(sys.stdin)
    befehl = daten.get("tool_input", {}).get("command", "")
    meldung = pruefe(befehl)
    if meldung:
        print(meldung, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
