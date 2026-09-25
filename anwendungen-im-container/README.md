# Lösung · Eigene Anwendungen im Container

Zwei Übungen, beide ohne vorgegebene Befehlsfolge: ein Skript in einem fremden
Image ausführen, dann eine Webanwendung betreiben, deren Abhängigkeit das Image
nicht mitbringt.

Zu den Übungen:
[Ein Python-Skript im Container ausführen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/anwendungen-im-container/issue.html)
·
[Eine Webanwendung mit Abhängigkeiten betreiben](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/anwendungen-im-container/issue-webapp.html)

## Ein Python-Skript ausführen

Mehrere Wege sind richtig. Der häufigste – das Arbeitsverzeichnis einhängen und
das Skript als Befehl übergeben:

```bash
# GIT BASH UNTER WINDOWS: Jedem Befehl, der ein Verzeichnis einhängt, ein
# MSYS_NO_PATHCONV=1 voranstellen – sonst baut die Shell den Pfad im Container
# zu einem Windows-Pfad um:  MSYS_NO_PATHCONV=1 docker container run ...

docker container run --rm -v "$(pwd)":/app python:3.12-slim python /app/hello.py
```

Ebenso richtig – die Datei in einen laufenden Container kopieren:

```bash
docker container run -d --name py python:3.12-slim sleep 300
docker container cp hello.py py:/hello.py
docker container exec py python /hello.py
docker container stop py && docker container rm py
```

**Der Aufruf ist wiederholbar**, und das ist der Punkt des Schalters: `--rm`
räumt den Container weg, und ohne `--name` kollidiert auch nichts. Wer einen
Namen vergibt und `--rm` weglässt, bekommt beim zweiten Lauf
`name is already in use`.

## Die Webanwendung mit Abhängigkeiten

```bash
# Abhängigkeiten installieren und starten – beides im selben Lauf,
# weil der Container mit --rm nach dem Ende verschwindet
docker container run --rm -p 8080:8080 -v "$(pwd)":/app -w /app python:3.12-slim \
  sh -c "pip install -r requirements.txt && python app.py"

curl http://localhost:8080
```

**Wenn kein Netzzugang aus dem Container erlaubt ist:** vorab ein Image mit Flask
bereitstellen und dessen Namen nennen, dann entfällt der `pip install`.

## Worauf es in der Nachbesprechung ankommt

1. Das Skript liegt **daneben**, nicht im Image. Das Image kennt es nicht – wer
   es weitergeben will, muss es mitschicken.
2. Flask wird bei **jedem** Start neu installiert – der Preis dafür, dass die
   Anwendung nicht im Image steckt. Das ist der Auftakt zu „Eigene Images bauen“.
3. `host="0.0.0.0"` ist Pflicht: Eine Anwendung, die nur auf `127.0.0.1` lauscht,
   ist trotz `-p` nicht erreichbar.
