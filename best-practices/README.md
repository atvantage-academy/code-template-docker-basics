# Lösung · Das Image optimieren

Zwei Eingriffe an einem Dockerfile, das schon funktioniert: die **Reihenfolge**,
damit der Build nicht jedes Mal alles neu installiert – und eine **zweite Stufe**,
damit der Container nichts mitschleppt, was er nur zum Bauen gebraucht hat.

Zur Übung:
[Das Image optimieren](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/best-practices/issue.html)

Ausgangspunkt ist das Dockerfile der Webanwendung aus `eigene-images-bauen/` –
dort steht `COPY . .` **vor** `RUN pip install`, und genau das wird hier
umgebaut. `app.py` und `requirements.txt` liegen unverändert daneben, damit sich
der Ordner für sich bauen lässt.

## Die Reihenfolge

```bash
# Vorher: eine Zeile in app.py ändern und mit dem ALTEN Dockerfile bauen
time docker image build -t meine-webapp:mess-1 .

# Umbauen (siehe Dockerfile), einmal bauen, damit der Cache den Aufbau kennt
docker image build -t meine-webapp:mess-2 .

# Nachher: wieder eine Zeile in app.py ändern und noch einmal messen
time docker image build -t meine-webapp:mess-3 .
```

Nachgemessen auf einem schnellen Rechner mit warmer Leitung:

| Lauf | Dockerfile | Zeit |
| --- | --- | --- |
| vorher | `COPY . .` vor `RUN pip install` | **2,3 s** |
| nachher | `requirements.txt` zuerst | **0,2 s** |

Die absoluten Zahlen sagen wenig – in der Schulungsumgebung dauert beides
länger. **Das Verhältnis ist der Ertrag:** Im zweiten Lauf meldet der
Installationsschritt `CACHED` und läuft gar nicht mehr. Geändert hat sich nur,
*wann* welche Datei ins Image kommt.

## Die zweite Stufe

```bash
docker image build -f Dockerfile.multistage -t meine-webapp:zwei-stufen .
docker image ls
```

| Image | Größe |
| --- | --- |
| einstufig | **174 MB** |
| zweistufig | **114 MB** |

Das zweistufige Image läuft genauso – gegen dieselbe Datenbank, mit denselben
`-e`-Angaben, mit derselben Antwort. Nur Python, `pip`, `pyinstaller` und die
Paketlisten sind nicht mehr darin.

### Zwei Stolpersteine, beide nachgemessen

1. **`pyinstaller` braucht `binutils`.** Ohne das Paket bricht die erste Stufe ab:
   `ERROR: On Linux, objdump is required.`
2. **Beide Stufen müssen auf derselben Debian-Fassung aufsetzen.** Mit
   `python:3.12-slim` oben (zeigt inzwischen auf eine neuere Fassung) und
   `debian:12-slim` unten baut das Image zwar, startet aber nicht:
   `Failed to load Python shared library … version 'GLIBC_2.38' not found`.
   Deshalb steht oben `python:3.12-slim-bookworm`.

   Das ist kein Python-Sonderfall: Ein Programm erwartet die Bibliotheken, gegen
   die es gebaut wurde.

## Worauf es in der Nachbesprechung ankommt

1. **Die Zahl laut sagen lassen.** Wer die Sekunden selbst gesehen hat, ordnet
   sein nächstes Dockerfile anders – wer nur die Regel gehört hat, nicht.
2. **Die Regel ist eine Folge, kein Merksatz:** Jede Schicht hängt am Hash der
   darunterliegenden. Was sich selten ändert, gehört nach vorn.
3. **Löschen macht nicht kleiner.** Deshalb hilft bei den Bauwerkzeugen kein
   `rm`, sondern nur eine Stufe, in der sie nie entstanden sind.
4. **Der Preis gehört dazu:** Die zweite Stufe kostet Bauzeit und ein weiteres
   Werkzeug in der Kette. Für ein Image, das selten ausgeliefert wird, lohnt sie
   nicht.

## Antworten auf die Reflexionsfragen

1. **Wie viel Zeit hat der Umbau gespart, und wobei genau?** Beim Installieren
   der Abhängigkeiten – der Schritt läuft nach einer Codeänderung gar nicht mehr,
   er kommt aus dem Cache. Alles andere bleibt, wie es war: dieselben Pakete,
   dasselbe Ergebnis, dieselbe Anwendung.
2. **Welchen Vorteil hat der Multi-Stage-Build?** Im Laufzeit-Image liegt nur
   noch das Ergebnis. Was nur zum Bauen nötig war, bleibt in der ersten Stufe –
   der Container überträgt es nicht mehr, hält es nicht vor und bietet es nicht
   als Angriffsfläche an. Mit einer `RUN`-Zeile wäre das nicht wegzubekommen:
   Was einmal in einer Schicht lag, bleibt darin. **Was in der letzten Stufe nie
   entstanden ist, muss auch nicht gelöscht werden.**

## Die Dateien dazu

### [`Dockerfile`](Dockerfile)

```dockerfile
FROM python:3.12-slim
WORKDIR /app

# Zuerst nur die Abhängigkeitsliste: Solange sie sich nicht ändert, bleibt die
# Installation im Cache – egal, wie oft app.py sich ändert.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python", "app.py"]
```

### [`Dockerfile.multistage`](Dockerfile.multistage)

```dockerfile
# Erste Stufe: bauen. Alles, was hier entsteht, bleibt hier – bis auf das
# eine Programm, das die zweite Stufe sich holt.
FROM python:3.12-slim-bookworm AS bau
WORKDIR /bau
RUN apt-get update \
 && apt-get install -y --no-install-recommends binutils \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pyinstaller
COPY app.py .
RUN pyinstaller --onefile app.py

# Zweite Stufe: laufen lassen. Kein Python, kein pip, kein pyinstaller.
# WICHTIG: dieselbe Debian-Fassung wie oben (bookworm), sonst passt die
# C-Bibliothek nicht zum gebauten Programm.
FROM debian:12-slim
COPY --from=bau /bau/dist/app /usr/local/bin/app
EXPOSE 8080
CMD ["app"]
```

Unverändert aus `eigene-images-bauen/webanwendung/` übernommen:

### [`app.py`](app.py)

```python
import os
from flask import Flask
import psycopg2

app = Flask(__name__)

# Konfiguration aus der Umgebung – die Werte dahinter gelten nur,
# solange nichts gesetzt ist.
DB_NAME = os.getenv("DB_NAME", "helloworld")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

@app.get("/")
def start():
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    cursor = connection.cursor()
    cursor.execute("SELECT text FROM gruss")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return "\n".join(row[0] for row in rows) + "\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### [`requirements.txt`](requirements.txt)

```text
flask==3.0.3
psycopg2-binary==2.9.13
```
