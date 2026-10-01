#!/usr/bin/env bash
#
# Gibt den Branch der Lösungskette aus, der am weitesten vorn steht – also den,
# auf dem alle anderen aufbauen. Weil jeder Lösungsbranch auf dem der vorigen
# Übung aufsetzt, liegen dort alle Lösungsordner beieinander.
#
# Aufruf:  spitze-ermitteln.sh [<arbeitsverzeichnis>]
#
# Gewertet wird, wie viele der anderen Branches ein Kandidat enthält. Das ist
# bewusst eine Mehrheit und kein Alles-oder-nichts: Während eine Kette umgebaut
# wird, hängen die hinteren Branches vorübergehend noch an der alten Basis, und
# dann gibt es keinen Branch, der wirklich alle enthält. Bei Gleichstand
# gewinnt der jüngste Commit.
set -euo pipefail

repo="${1:-.}"

mapfile -t branches < <(
  git -C "$repo" for-each-ref --format='%(refname:short)' 'refs/remotes/origin/loesung/*'
)
if [ "${#branches[@]}" -eq 0 ]; then
  echo "Kein Branch unter origin/loesung/ gefunden." >&2
  exit 1
fi

spitze=""
bestwert=-1
bestzeit=0

for kandidat in "${branches[@]}"; do
  enthalten=0
  for anderer in "${branches[@]}"; do
    [ "$kandidat" = "$anderer" ] && continue
    if git -C "$repo" merge-base --is-ancestor "$anderer" "$kandidat"; then
      enthalten=$((enthalten + 1))
    fi
  done
  zeit=$(git -C "$repo" log -1 --format=%ct "$kandidat")
  echo "  ${kandidat#origin/}: enthält $enthalten der ${#branches[@]} Branches" >&2

  if [ "$enthalten" -gt "$bestwert" ] ||
     { [ "$enthalten" -eq "$bestwert" ] && [ "$zeit" -gt "$bestzeit" ]; }; then
    spitze="$kandidat"
    bestwert="$enthalten"
    bestzeit="$zeit"
  fi
done

echo "${spitze#origin/}"
