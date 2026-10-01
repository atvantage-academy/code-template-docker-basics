# Lösung · Eigene Images bauen

Was bisher von außen eingehängt wurde, wandert ins Image – erst eine Webseite,
dann die Anwendung samt ihren Abhängigkeiten. Danach gibt man ein Artefakt
weiter statt einer Anleitung.

Zu den Übungen:
[Ein eigenes Image bauen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/eigene-images-bauen/issue.html)
·
[Die Webanwendung als eigenes Image](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/eigene-images-bauen/issue-webapp.html)
·
[Ein Image versioniert in eine Registry pushen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/eigene-images-bauen/issue-veroeffentlichen.html)

## Ein eigenes Image bauen

Die eigene Seite wandert ins Image. Die `index.html` ist dieselbe wie in
`container-verwalten/` – dort hat der Container sie noch eingehängt bekommen.

### Die Befehle in der Reihenfolge

```bash
# Die Shell steht in dem Verzeichnis, in dem das Dockerfile liegt.

# 1. Ohne Namen bauen – und das Ergebnis suchen
docker image build .
docker image ls                              # das eigene Image fehlt hier

# Es ist gebaut, aber namenlos. Je nach Docker-Fassung findet man es so:
docker image ls --filter dangling=true

# 2. Mit Namen und Version bauen
docker image build -t meine-website:1.0.0 .
docker image ls

# 3. Einen Container daraus betreiben
docker container create --name website -p 8080:80 meine-website:1.0.0
docker container start website

curl http://localhost:8080                   # die eigene Seite
curl http://localhost:8080/gebaut.html       # die beim Bauen entstandene

# 4. Die Seite ändern – und sehen, was dafür nötig ist
#    Ein restart reicht NICHT, auch nicht nach einem neuen Bau.
docker container stop website
docker container rm website
docker image build -t meine-website:1.0.0 .
docker container create --name website -p 8080:80 meine-website:1.0.0
docker container start website
curl http://localhost:8080                   # jetzt die neue Fassung

# 5. Aufräumen – das Verzeichnis bleibt stehen, es wird noch gebraucht
docker container stop website
docker container rm website
```

### Was ein Bau ohne `-t` hinterlässt

Nachgemessen mit Docker 29.8.0: Das Image taucht in `docker image ls`
**gar nicht** auf. Zu finden ist es erst mit
`docker image ls --filter dangling=true`, und dort heißt es `<untagged>`.
Ältere Fassungen listen es in `docker image ls` als `<none>:<none>`.

In beiden Fällen gilt dasselbe: Das Image ist fertig und über seine ID nutzbar,
aber niemand findet es wieder. Wer dreimal ohne `-t` baut, hat drei davon – das
sind die *dangling images*.

### Worauf es in der Nachbesprechung ankommt

1. **Zwei Sorten Zeilen, zwei Zeitpunkte.** `COPY` und `RUN` laufen **beim
   Bauen** und verändern das Image. `EXPOSE` verändert nichts – es schreibt eine
   Angabe ins Image, die erst **beim Starten** gelesen wird. Ein Paar sein
   Dockerfile zeigen lassen und die anderen raten lassen, welche Zeile wann
   läuft.
2. **Der Build-Kontext ist das Verzeichnis, nicht die Datei.** Der Punkt am Ende
   schickt alles mit, was dort liegt. Deshalb steht die Shell in diesem
   Verzeichnis, und deshalb gehört dort nichts hin, was nicht ins Image soll.
3. **`EXPOSE` öffnet nichts.** Gegenprobe vorführen: Container ohne `-p` starten,
   nichts ist erreichbar – obwohl `EXPOSE 80` im Dockerfile steht.
4. **Das Verzeichnis bleibt stehen.** Die beiden folgenden Übungen bauen darauf
   auf.

### Antworten auf die Reflexionsfragen

1. **Was passiert ohne `-t`?** Siehe oben: Das Image bekommt keinen Namen und ist
   praktisch unauffindbar. Der Name ist kein Schmuck, sondern die einzige Art,
   ein Image später wieder anzusprechen – beim Starten, beim Weitergeben, beim
   Aufräumen.
2. **Was ist nötig, bis eine geänderte `index.html` per HTTP zu sehen ist?**
   Container **stoppen**, Container **löschen**, Image **neu bauen**, Container
   **neu erzeugen**, Container **starten**. Nachgemessen: Ein `restart` genügt
   nicht – auch dann nicht, wenn vorher neu gebaut wurde. Der Container hängt an
   der Fassung des Images, aus der er erzeugt wurde; ein Image ändert sich nicht,
   es entsteht ein neues.

   **Das Gegenbild steht in der ersten Übung:** Beim dritten Container, der das
   Verzeichnis eingehängt bekam, reichte das Speichern der Datei. Der eine Weg
   ist bequem beim Entwickeln, der andere ergibt ein Artefakt, das man
   weitergeben kann – und genau darum geht es ab jetzt.
3. **Wofür wird `EXPOSE` verwendet?** Als **Dokumentation im Image**: „Hier
   lausche ich.“ Wer das Image bekommt, muss nicht raten, welchen Port er
   veröffentlichen soll. Veröffentlicht wird er damit nicht – das entscheidet
   `-p` beim Erzeugen des Containers.
4. **`ENTRYPOINT`, `CMD`, `RUN`?** `RUN` läuft **beim Bauen** und verändert das
   Image – alles, was es anlegt, steckt danach darin. `ENTRYPOINT` ist das
   Programm, das **beim Starten** läuft. `CMD` liefert dessen Standardargumente
   und wird von dem überschrieben, was hinter dem Imagenamen steht.
5. **Wofür `HEALTHCHECK`?** Das Image sagt selbst, woran man erkennt, dass es
   arbeitet. Docker zeigt den Zustand an, eine Plattform kann daraufhin neu
   starten oder Verkehr umleiten. „Der Prozess läuft“ reicht als Aussage nicht:
   Ein Prozess kann leben und trotzdem keine Anfrage mehr beantworten – genau
   diesen Fall soll die Prüfung erwischen.

### Die Dateien dazu

#### [`Dockerfile`](Dockerfile)

```dockerfile
FROM nginx:1.27.5
COPY index.html /usr/share/nginx/html/index.html
RUN echo "<h1>Beim Bauen entstanden</h1>" > /usr/share/nginx/html/gebaut.html
EXPOSE 80
```

#### [`index.html`](index.html)

```html
<h1>Diese Seite liegt auf meinem Rechner</h1>
```

## Die Webanwendung als eigenes Image

Dieselbe Anwendung wie in `anwendung-und-datenbank/` – nur kommt sie jetzt nicht
mehr aus einem eingehängten Verzeichnis, sondern aus einem Image. `app.py` und
`requirements.txt` sind unverändert und liegen in `webanwendung/` noch einmal
daneben, damit der Ordner für sich gebaut werden kann.

```bash
# Die Shell steht in webanwendung/.
docker image build -t meine-webapp:1.0.0 .

# Das Netzwerk und die Datenbank aus der vorigen Übung laufen weiter.
docker container run -d \
  --name meine-webapp \
  --network helloworld-network \
  -p 8080:8080 \
  -e DB_HOST=meine-db \
  -e DB_NAME=helloworld \
  -e DB_USER=kurs \
  -e DB_PASSWORD=geheim \
  meine-webapp:1.0.0

curl http://localhost:8080
```

Nachgemessen: Drei Zeilen aus der Tabelle `gruss`, das Image ist rund 166 MB
groß. **Das `-v "$(pwd)":/app` von gestern ist weg** – der Code steckt jetzt im
Artefakt, und der Startbefehl ist eine einzige Zeile.

### Dieses Dockerfile ist absichtlich noch nicht gut

`COPY . .` steht **vor** `RUN pip install`. Damit liegt der Anwendungscode in
derselben Schicht wie alles andere, und jede Änderung an `app.py` macht die
Installation der Abhängigkeiten ungültig. Nachgemessen mit
`docker image build --progress=plain`: Der Installationsschritt läuft nach jeder
Änderung erneut.

**Das ist so gewollt.** Die Übung *Das Image optimieren* in Block 7 baut genau
dieses Dockerfile um – wer hier schon die gute Reihenfolge schreibt, nimmt der
Messung dort ihren Gegenstand. Wer es von selbst besser macht, hat recht; dann
gibt es in Block 7 ein anderes Beispiel.

### Worauf es in der Nachbesprechung ankommt

1. **Im Dockerfile steht keine Datenbankadresse.** Sie kommt mit `-e` beim
   Erzeugen des Containers. Wer sie einbackt, braucht ein Image je Umgebung.
2. **Was gibt man jetzt noch weiter?** Den Namen des Images und den Startbefehl.
   Mehr nicht – aus Paket plus Anleitung ist ein Artefakt geworden.
3. **`CMD` erwartet eine Liste.** `CMD "python app.py"` startet eine Shell und
   führt zu überraschenden Signalproblemen; `CMD ["python", "app.py"]` ist die
   Form, die gemeint ist.

### Antworten auf die Reflexionsfragen

1. **Gehört die Adresse der Datenbank ins Dockerfile?** Nein – sie gehört an den
   Container. Ins Image kommt, was in jeder Umgebung gleich ist: Laufzeit,
   Abhängigkeiten, Code, Startbefehl, Port. Beim Start kommt dazu, was die
   Umgebung bestimmt: Adresse, Zugangsdaten, Port-Weitergabe. **Die Grenze
   verläuft dort, wo die Umgebung ins Spiel kommt.** Eine eingebackene Adresse
   kostet ein Image je Umgebung – drei Artefakte, von denen eines getestet ist.
2. **Wozu dann `ENV`?** Für einen **Standardwert**, damit das Image ohne Zutun
   startet – in `app.py` tun das die Vorgaben in `os.getenv(...)`, im Dockerfile
   täte es `ENV`. `-e` beim Start sticht ihn. Das ist kein Widerspruch zur
   Konfiguration von außen, sondern ihre praktische Form: sinnvolle Vorgabe im
   Image, echter Wert aus der Umgebung.

### Die Dateien dazu

#### [`webanwendung/Dockerfile`](webanwendung/Dockerfile)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["python", "app.py"]
```

Unverändert aus `anwendung-und-datenbank/` übernommen:

#### [`webanwendung/app.py`](webanwendung/app.py)

```python
import os
from flask import Flask
import psycopg2

app = Flask(__name__)

# Konfiguration aus der Umgebung – die Werte dahinter gelten nur,
# solange nichts gesetzt ist.
DB_NAME = os.getenv("DB_NAME", "helloworld")
DB_USER = os.getenv("DB_USER", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Das Passwort darf auch aus einer Datei kommen: DB_PASSWORD_FILE nennt den Pfad.
PASSWORD_FILE = os.getenv("DB_PASSWORD_FILE")
if PASSWORD_FILE:
    with open(PASSWORD_FILE) as datei:
        DB_PASSWORD = datei.read().strip()
else:
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

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

#### [`webanwendung/requirements.txt`](webanwendung/requirements.txt)

```text
flask==3.0.3
psycopg2-binary==2.9.13
```

## Ein Image versioniert in eine Registry pushen

Hier gibt es nichts zu kopieren – die Übung besteht aus Befehlen, und die Namen
darin hängen an Deiner Registry. `<registry>` ist deren Adresse (für Docker Hub
entfällt sie), `<deine-org>` die Organisation darin.

```bash
docker login <registry>

# Zwei Namen gleich beim Bauen – das spart den Umweg über docker image tag
docker image build \
  -t meine-website:1.0.0 \
  -t <deine-org>/meine-website:1.0.0 \
  .

docker image ls          # ein Image, zwei Namen: dieselbe IMAGE ID

docker image push <deine-org>/meine-website:1.0.0

# Der bewegliche Zeiger daneben
docker image tag meine-website:1.0.0 <deine-org>/meine-website:latest
docker image push <deine-org>/meine-website:latest

# Zweite Fassung: Seite ändern, neu bauen, pushen – und erst DANN latest nachziehen
echo '<h1>Meine Seite, dritte Fassung</h1>' > index.html
docker image build -t <deine-org>/meine-website:1.0.1 .
docker image push <deine-org>/meine-website:1.0.1

docker image tag <deine-org>/meine-website:1.0.1 <deine-org>/meine-website:latest
docker image push <deine-org>/meine-website:latest

# Optional: lokal wegräumen und die veröffentlichte Fassung zurückholen
docker image rm <deine-org>/meine-website:1.0.0 <deine-org>/meine-website:latest
docker image pull <deine-org>/meine-website:1.0.0
```

### Was dabei in der Registry passiert

Gegen eine lokale Registry (`registry:2`) nachgemessen. Danach liegen dort drei
Tags, aber nur **zwei** verschiedene Images:

| Tag | Digest |
| --- | --- |
| `1.0.0` | `sha256:57842b2a…` |
| `1.0.1` | `sha256:6cd4ffa9…` |
| `latest` | `sha256:6cd4ffa9…` |

`latest` und `1.0.1` sind **dasselbe Image unter zwei Namen** – deshalb ist der
zweite Push auch so schnell: Es ist nichts zu übertragen, nur ein Name zu setzen.
Und `1.0.0` liegt unberührt daneben; genau das macht ein Zurückrollen möglich.

### Worauf es in der Nachbesprechung ankommt

1. **Ein Image, mehrere Namen.** `docker image tag` baut nichts, es benennt. Die
   `IMAGE ID` bleibt dieselbe – am besten vorführen.
2. **Der Name ist die Adresse.** Registry, Organisation, Repository, Tag. Wer
   woanders hin will, muss das Image umbenennen, nicht neu bauen.
3. **Reihenfolge beim Nachziehen:** erst die neue Version veröffentlichen, dann
   `latest` darauf zeigen lassen. Wer `latest` zuerst verschiebt, hat einen
   Zeiger auf etwas, das in der Registry noch nicht liegt.
4. **Der zweite Push ist schnell, weil nichts übertragen wird.** Die Schichten
   liegen schon dort. Das ist derselbe Mechanismus wie beim Build-Cache – und
   der Übergang zu Block 7.

### Antworten auf die Reflexionsfragen

1. **Wie kommt `latest` an ein bereits gepushtes Image?** Mit
   `docker image tag` und einem zweiten Push. **Neu gebaut wird nichts** – der
   Tag ist ein Name auf einem Image, das es schon gibt.
2. **Welche Schritte für `1.0.1` samt `latest`?** Ändern, bauen mit `-t …:1.0.1`,
   pushen, `latest` auf `1.0.1` taggen, `latest` pushen.
3. **Was passiert, wenn es nur `latest` gibt?** Die Registry hält dann nur den
   jeweils letzten Stand unter einem Namen, der sich bewegt. Niemand kann sagen,
   welche Fassung gestern lief, und es gibt nichts, worauf man zurückgehen
   könnte. Wer gestern gezogen hat, hat etwas anderes bekommen als heute –
   dieselbe Angabe, ein anderes Ergebnis.
4. **Warum war der zweite Push schneller?** Weil die Schichten schon in der
   Registry lagen. Übertragen wurde nur das Manifest; der Rest war ein
   Namenseintrag.
5. **`FROM` ohne Tag?** Dann gilt `latest` – und das zeigt in einem halben Jahr
   woanders hin. Derselbe Build ergibt dann ein anderes Image, ohne dass sich im
   Dockerfile etwas geändert hat. Ein fester Tag ist die Bedingung dafür, dass
   ein Build wiederholbar ist.
