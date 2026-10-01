# Lösung · Eigene Anwendungen im Container

Das Modul hat zwei Übungen, und jede hat ihren eigenen Pull Request. Dieser hier
gehört zur ersten: ein fertiges Skript in einem fremden Image ausführen, ohne
etwas zu installieren und ohne einen Container zurückzulassen.

Zur Übung:
[Ein Python-Skript im Container ausführen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/anwendungen-im-container/issue.html)

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

## Worauf es in der Nachbesprechung ankommt

1. **Das Skript liegt daneben, nicht im Image.** Das Image kennt es nicht – wer
   es weitergeben will, muss es mitschicken.
2. **Zwei verschiedene Lösungen zeigen lassen**, nicht die „richtige“. Dass
   mehrere Wege ans Ziel führen, ist Teil der Lektion.

## Die Dateien dazu

### [`hello.py`](hello.py)

```python
print("Hallo aus dem Container!")
```
