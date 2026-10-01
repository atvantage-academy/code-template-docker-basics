# Lösung · Eigene Anwendungen im Container

Ein fertiges Skript und eine Webanwendung in einem fremden Image laufen lassen –
ohne etwas zu installieren und ohne ein eigenes Image zu bauen.

Das Modul hat zwei Übungen, und jede hat ihren eigenen Pull Request. Dieser hier
kommt zur zweiten dazu: die Webanwendung, deren Abhängigkeit das fremde Image
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

1. **Das Skript liegt daneben, nicht im Image.** Das Image kennt es nicht – wer
   es weitergeben will, muss es mitschicken.
2. **Zwei verschiedene Lösungen zeigen lassen**, nicht die „richtige“. Dass
   mehrere Wege ans Ziel führen, ist Teil der Lektion.
3. **Flask wird bei jedem Start neu installiert** – der Preis dafür, dass die
   Anwendung nicht im Image steckt. Das ist der Auftakt zu „Eigene Images bauen“,
   und in Block 3 bekommt es seinen Namen: die Station *Bauen*, im Nachschlagewerk
   Faktor II (*Dependencies*).
4. **`host="0.0.0.0"` ist Pflicht:** Eine Anwendung, die nur auf `127.0.0.1`
   lauscht, ist trotz `-p` nicht erreichbar.

## Antworten auf die Reflexionsfragen der Webanwendung

1. **Wann wird Flask installiert, und wie oft?** Beim Start des Containers – also
   bei **jedem** Lauf, denn mit `--rm` ist der Container danach weg. Die
   Installation lebt im Container, nicht im Image. Das kostet jedes Mal Zeit und
   setzt voraus, dass aus dem Container heraus Pakete geladen werden dürfen.
2. **Warum `0.0.0.0` und nicht `127.0.0.1`?** `127.0.0.1` ist die
   Loopback-Adresse **im Container**: Dort erreicht die Anwendung nur, wer selbst
   im Container ist. Von außen kommt nichts an, auch nicht über `-p` – die
   Weitergabe endet an einer Adresse, auf der niemand lauscht. `0.0.0.0` heißt
   „auf allen Adressen des Containers“, und erst damit greift die Port-Weitergabe.

## Die Dateien dazu

### [`hello.py`](hello.py)

```python
print("Hallo aus dem Container!")
```

### [`app.py`](app.py)

```python
from flask import Flask

app = Flask(__name__)

@app.get("/")
def start():
    return "Hallo aus der Webanwendung!\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### [`requirements.txt`](requirements.txt)

```text
flask==3.0.3
```
