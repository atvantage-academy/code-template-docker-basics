# Lösung · Die ganze Landschaft mit einem Befehl starten

Fünfzehn `docker`-Aufrufe werden eine Datei. Was darin steht, kennt die Gruppe
schon: Images, Umgebungsvariablen, Volumes, Ports. **Compose ist kein neues
Konzept, sondern eine Schreibweise.**

Zur Übung:
[Die ganze Landschaft mit einem Befehl starten](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/mehrere-container/issue.html)

Das Image `meine-webapp:1.0.0` stammt aus `best-practices/` – dort liegen
`Dockerfile`, `app.py` und `requirements.txt`.

## Die Befehle in der Reihenfolge

```bash
# Die Container der vorigen Übungen belegen Namen und Ports.
docker container rm -f meine-db meine-webapp

# Das Passwort steht nicht in der compose.yaml, sondern in einer .env daneben –
# und den Wert würfelt die Shell aus.
echo "DB_PASSWORD=$(openssl rand -base64 18)" > .env

docker compose up -d
docker compose ps

# Was beim Start passiert ist: die Zeilen zu schema.sql, dann
# "database system is ready to accept connections"
docker compose logs datenbank

# Weder angelegt noch in der Datei genannt – und trotzdem da:
docker network ls          # mehrere-container_default
docker volume ls           # mehrere-container_helloworld-data

curl http://localhost:8080

# Container weg, Volume bleibt
docker compose down
```

Nachgemessen: `curl` liefert die drei Zeilen aus `schema.sql`. Nach
`docker compose down` und erneutem `up -d` sind sie – samt einer selbst
eingefügten Zeile – wieder da.

## Drei Dinge, die hier anders sind als in den Einzelbefehlen

1. **Kein `docker network create`.** Compose legt für das Projekt ein Netzwerk an
   und trägt jeden Service unter seinem **Servicenamen** ein. Deshalb steht in
   `DB_HOST` jetzt `datenbank` und nicht `meine-db`. Der mühsame Netzwerkteil vom
   Vormittag fällt ersatzlos weg.
2. **Kein veröffentlichter Port an der Datenbank.** Sie ist nur innerhalb des
   Projekts erreichbar – und das genügt.
3. **Die Namen kommen aus dem Projekt**, und das Projekt heißt nach dem
   Verzeichnis: `mehrere-container_default`, `mehrere-container_helloworld-data`.
   Wer dasselbe in einem anderen Verzeichnis startet, bekommt eine zweite,
   unabhängige Landschaft.

## Das Passwort: Datei statt Wert

Die Datenbank liest es über `POSTGRES_PASSWORD_FILE` aus `/run/secrets/db-passwort`.
Compose legt diese Datei an; ihren Inhalt bezieht sie aus der Umgebung, also aus
der `.env`. Damit steht der Wert an **einer** Stelle – nicht in der
`compose.yaml` und nicht im Repository (die `.env` ist in `.gitignore`).

**Die ehrliche Grenze:** Die Webanwendung bekommt denselben Wert weiterhin als
Umgebungsvariable, weil `app.py` keine Passwortdatei lesen kann. Das ist der
Grund, warum Anwendungen diese Fähigkeit mitbringen sollten – benennen, nicht
vertiefen.

## Freiwillig: wirklich warten statt nur starten

`depends_on` wartet auf den **Start** der Datenbank, nicht auf ihre
**Bereitschaft**. Mit einem `healthcheck` und `condition: service_healthy` wartet
Compose wirklich:

```bash
docker compose -f compose.yaml -f compose.healthcheck.yaml up -d
```

Nachgemessen – die Ausgabe sagt es selbst:

```text
Container mehrere-container-datenbank-1  Healthy
Container mehrere-container-webapp-1     Started
```

**Trotzdem ist das nur die halbe Antwort.** Die robustere ist eine Anwendung, die
es erneut versucht, wenn die Datenbank kurz fehlt – auf einer Plattform ist das
der Normalfall, nicht die Ausnahme.

## Worauf es in der Nachbesprechung ankommt

1. **Die Datei vorlesen lassen.** Eine gute Compose-Datei ist ohne Erklärung
   verständlich – genau deshalb ist sie die bessere Übergabe als eine
   Befehlsliste.
2. **Nichts Neues, nur anders aufgeschrieben.** Jeder Schlüssel hat seinen
   Parameter von gestern: `-e` → `environment`, `-p` → `ports`, `-v` → `volumes`,
   `--name` → Servicename.
3. **`down` gegen `down -v`.** Ersteres räumt Container weg, Letzteres auch die
   Daten. Diese Verwechslung kostet echte Volumes.

## Antworten auf die Reflexionsfragen

1. **Welchen Zweck hat Docker Compose?** Es beschreibt eine **ganze Landschaft in
   einer Datei**, statt sie aus einer Befehlsgeschichte aufzubauen. Daraus folgt
   der Rest: Ein Befehl startet und stoppt sie. Das Netzwerk legt Compose selbst
   an und trägt jeden Service unter seinem Namen ein. Und die Datei ist die
   Übergabe – eine neue Kollegin braucht sie und sonst nichts. Die Konzepte
   bleiben dieselben; sie stehen nur nicht mehr in fünfzehn Aufrufen, sondern an
   einer Stelle, die man lesen, prüfen und versionieren kann.

## Die Dateien dazu

### [`compose.yaml`](compose.yaml)

```yaml
services:

  datenbank:
    image: postgres:16
    environment:
      POSTGRES_USER: kurs
      POSTGRES_DB: helloworld
      # Das Passwort kommt als Datei herein, nicht als Wert.
      POSTGRES_PASSWORD_FILE: /run/secrets/db-passwort
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - helloworld-data:/var/lib/postgresql/data
      # Läuft beim ERSTEN Start, wie in "Eine Datenbank konfigurieren".
      - ./schema.sql:/docker-entrypoint-initdb.d/1-schema.sql:ro
    secrets:
      - db-passwort

  webapp:
    image: meine-webapp:1.0.0
    environment:
      DB_HOST: datenbank
      DB_NAME: helloworld
      DB_USER: kurs
      DB_PASSWORD: ${DB_PASSWORD}
    ports:
      - "8080:8080"
    depends_on:
      - datenbank

volumes:
  helloworld-data:

secrets:
  db-passwort:
    environment: DB_PASSWORD
```

### [`compose.healthcheck.yaml`](compose.healthcheck.yaml)

```yaml
# Der freiwillige Teil: wirklich warten statt nur starten.
# Aufruf:  docker compose -f compose.yaml -f compose.healthcheck.yaml up -d
services:

  datenbank:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kurs -d helloworld"]
      interval: 5s
      retries: 10

  webapp:
    depends_on:
      datenbank:
        condition: service_healthy
```

### [`schema.sql`](schema.sql)

Unverändert aus `konfiguration-und-zustand/`.

```sql
CREATE TABLE gruss (
  id   SERIAL PRIMARY KEY,
  text TEXT NOT NULL
);

INSERT INTO gruss (text)
VALUES ('Hallo Welt'), ('Hello World'), ('Bonjour le monde');
```
