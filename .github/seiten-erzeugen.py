#!/usr/bin/env python3
"""Erzeugt aus den Lösungsordnern eines Branches die Seiten für GitHub Pages.

Aufruf:  seiten-erzeugen.py <quelle> <ziel> [<branchname>]

Die Quelle ist ein Arbeitsverzeichnis des Lösungsbranches, das Ziel die Wurzel
der Jekyll-Quellen. Jeder Ordner darin, der eine README.md enthält, wird zu
einer Seite «ordner»/index.md; alle weiteren Dateien des Ordners landen unter
«ordner»/dateien/, und die Verweise darauf werden mitgezogen.

Der Umweg über dateien/ ist nötig, weil ein Artefakt sonst die Seite überschreibt:
Eine Lösung mit eigener index.html – und die gibt es, sobald Webseiten im Spiel
sind – läge sonst genau dort, wo die gebaute Seite liegt.

Bewusst generisch: Es gibt keine Liste der Module. Wer einen Lösungsordner
hinzufügt, bekommt seine Seite ohne weiteres Zutun. Die Reihenfolge stammt aus
der Git-Historie – der Ordner, der zuerst angelegt wurde, steht oben.
"""

import os
import re
import shutil
import subprocess
import sys


def erster_titel(text):
    for zeile in text.splitlines():
        if zeile.startswith("# "):
            return zeile[2:].strip()
    return None


def erster_absatz(text):
    # Der erste Absatz nach der Überschrift, einzeilig und ohne Markdown-Links.
    nach_titel = re.sub(r"\A.*?^# .*?$", "", text, count=1, flags=re.S | re.M)
    for block in nach_titel.strip().split("\n\n"):
        block = " ".join(block.split())
        if block and not block.startswith(("#", ">", "```", "|", "-", "*")):
            block = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", block)
            return re.sub(r"[*_`]+", "", block)
    return None


def anlagedatum(quelle, ordner):
    """Zeitpunkt des Commits, der den Ordner angelegt hat – oder 0."""
    try:
        ausgabe = subprocess.run(
            ["git", "log", "--reverse", "--format=%ct", "--diff-filter=A", "--", ordner],
            cwd=quelle, capture_output=True, text=True, check=True,
        ).stdout.split()
        return int(ausgabe[0]) if ausgabe else 0
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return 0


def yaml_text(wert):
    return '"' + wert.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    if len(sys.argv) < 3:
        sys.exit("Aufruf: seiten-erzeugen.py <quelle> <ziel> [<branchname>]")
    quelle, ziel = sys.argv[1], sys.argv[2]
    branch = sys.argv[3] if len(sys.argv) > 3 else ""

    ordner = sorted(
        name for name in os.listdir(quelle)
        if not name.startswith(".")
        and os.path.isfile(os.path.join(quelle, name, "README.md"))
    )
    if not ordner:
        sys.exit(f"Kein Lösungsordner mit README.md unter {quelle} gefunden.")

    ordner.sort(key=lambda name: (anlagedatum(quelle, name), name))

    for nummer, name in enumerate(ordner, start=1):
        quellordner = os.path.join(quelle, name)
        zielordner = os.path.join(ziel, name)
        os.makedirs(zielordner, exist_ok=True)

        text = open(os.path.join(quellordner, "README.md"), encoding="utf-8").read()
        titel = erster_titel(text) or name
        beschreibung = erster_absatz(text)
        # Die Überschrift rendert das Layout; im Inhalt wäre sie doppelt.
        rumpf = re.sub(r"\A.*?^# .*?$\n*", "", text, count=1, flags=re.S | re.M)

        kopf = [
            "---",
            "layout: default",
            "kategorie: loesung",
            f"reihenfolge: {nummer}",
            f"title: {yaml_text(titel)}",
        ]
        if beschreibung:
            kopf.append(f"beschreibung: {yaml_text(beschreibung)}")
        kopf.append("---")

        # Die übrigen Artefakte nach dateien/ kopieren und die Verweise
        # darauf mitziehen.
        artefakte = []
        for wurzel, _, dateinamen in os.walk(quellordner):
            for dateiname in dateinamen:
                if wurzel == quellordner and dateiname == "README.md":
                    continue
                voll = os.path.join(wurzel, dateiname)
                relativ = os.path.relpath(voll, quellordner).replace(os.sep, "/")
                zielpfad = os.path.join(zielordner, "dateien", *relativ.split("/"))
                os.makedirs(os.path.dirname(zielpfad), exist_ok=True)
                shutil.copy2(voll, zielpfad)
                artefakte.append(relativ)

        # Längste zuerst, damit "website/index.html" vor "index.html" drankommt.
        for relativ in sorted(artefakte, key=len, reverse=True):
            rumpf = rumpf.replace(f"]({relativ})", f"](dateien/{relativ})")

        with open(os.path.join(zielordner, "index.md"), "w", encoding="utf-8") as datei:
            datei.write("\n".join(kopf) + "\n\n" + rumpf)

        print(f"{nummer:2d}. {name} – {titel} ({len(artefakte)} Artefakt(e))")

    if branch:
        with open(os.path.join(ziel, "_config.yml"), "a", encoding="utf-8") as datei:
            datei.write(f"\nloesungs_branch: {yaml_text(branch)}\n")


if __name__ == "__main__":
    main()
