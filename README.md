# Musterlösungen · Docker-Grundlagen

Dieses Repository hält die **Musterlösungen** zu den Übungen der Schulung
„Docker-Grundlagen“ der ATVANTAGE Academy. Die Übungen selbst stehen in den
[Lernenden-Unterlagen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/).

**Sieh hier erst nach, wenn Du es selbst versucht hast.** Der Wert einer Übung
liegt im Suchen, nicht im Ergebnis – und im Kurs wird nach dem Weg gefragt, nicht
nach der Lösung.

## Eine Lösung ist ein Branch, kein Ordner

Die Übungen bauen aufeinander auf – vom ersten fremden Container bis zur
Landschaft, die mit einem Befehl startet. Genau so liegen die Lösungen hier:
Jede Übung hat einen Branch, und dieser Branch baut auf dem der **vorherigen**
Übung auf.

```text
main                                   ← nur Rahmen: .gitignore, README
 └─ loesung/container-verwalten        ← Stand nach der ersten Übung
     └─ loesung/anwendungen-im-container
         └─ loesung/konfiguration-und-zustand
             └─ loesung/anwendung-und-datenbank
                 └─ loesung/eigene-images-bauen
                     └─ loesung/best-practices
                         └─ loesung/mehrere-container
```

Der Branch-Name ist `loesung/<modul>`; `<modul>` ist der Ordner der Übung im
Konzept-Repo (ohne die führende Nummer). Die **Reihenfolge** steht nicht im
Namen – sie ergibt sich aus der Reihenfolge der Übungen in
`docker-grundlagen/index.md`.

Wer die Lösung zu einer Übung sucht, checkt deren Branch aus. Dort steht der
Stand **nach** dieser Übung: alles, was die Übungen davor aufgebaut haben, plus
das Neue.

## Was hier liegt – und was nicht

In einem Docker-Kurs ist die Lösung selten eine Datei. Deshalb steht in jedem
Branch eine **`befehle.md`**: die Befehle in der Reihenfolge, in der sie laufen,
mit einer Zeile Begründung dort, wo sie nicht selbsterklärend sind. Das ist
dieselbe Datei, die die Lernenden ab der dritten Übung selbst führen.

Dazu kommen die Dateien, die in der jeweiligen Übung entstehen – `hello.py`,
`app.py`, `requirements.txt`, `Dockerfile`, `compose.yaml`.

**Nicht hier:** Zugangsdaten, Registry-Konten, kundenspezifische Adressen. Die
Passwörter in den Beispielen (`geheim`) sind Kursmaterial und ausdrücklich keine
Empfehlung.

## Der Anwendungscode wird gestellt, nicht geschrieben

Die Lernenden programmieren in diesem Kurs nicht. `hello.py` und `app.py` stehen
vollständig in der jeweiligen Übungsbeschreibung; sie liegen hier zum Kopieren –
und damit der Trainer sie schnell zur Hand hat, etwa um sie vorab in ein Image zu
backen, wenn die Umgebung kein `pip install` zulässt.
