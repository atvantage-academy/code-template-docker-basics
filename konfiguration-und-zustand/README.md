# Lösung · Eine Datenbank konfigurieren

Eine fremde Datenbank vollständig von außen einrichten – ohne Dockerfile, ohne
Konfigurationsdatei im Image. Und die Daten so ablegen, dass sie den Container
überleben.

Zur Übung:
[Eine Datenbank konfigurieren](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/konfiguration-und-zustand/issue.html)

## Die Befehle in der Reihenfolge

```bash
# GIT BASH UNTER WINDOWS: Jedem Befehl, der eine Datei oder ein Verzeichnis
# einhängt, ein MSYS_NO_PATHCONV=1 voranstellen – sonst baut die Shell den Pfad
# im Container zu einem Windows-Pfad um.

# 1. Ohne Konfiguration – der Container startet nicht, und die Logs sagen warum
docker container run -d --name meine-db postgres:16
docker container logs meine-db          # Database is uninitialized and superuser password is not specified
docker container rm meine-db

# 2. Alles kommt von außen dazu
docker container run -d \
  --name meine-db \
  -p 5432:5432 \
  -e POSTGRES_DB=helloworld \
  -e POSTGRES_USER=kurs \
  -e POSTGRES_PASSWORD=geheim \
  postgres:16

docker container logs meine-db          # ... database system is ready to accept connections

# 3. Das Schema als Datei hineinreichen – es läuft beim ERSTEN Start
docker container stop meine-db && docker container rm meine-db

docker container run -d \
  --name meine-db \
  -p 5432:5432 \
  -e POSTGRES_DB=helloworld \
  -e POSTGRES_USER=kurs \
  -e POSTGRES_PASSWORD=geheim \
  -v "$(pwd)/schema.sql":/docker-entrypoint-initdb.d/1-schema.sql \
  postgres:16

# Die Probe – und nur dafür – von innen
docker container exec meine-db psql -U kurs -d helloworld -c "SELECT * FROM gruss"

# 4. Die Daten in ein Volume, damit sie den Container überdauern
docker volume create kurs-daten
docker container stop meine-db && docker container rm meine-db

docker container run -d \
  --name meine-db \
  -p 5432:5432 \
  -e POSTGRES_DB=helloworld \
  -e POSTGRES_USER=kurs \
  -e POSTGRES_PASSWORD=geheim \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v kurs-daten:/var/lib/postgresql/data \
  -v "$(pwd)/schema.sql":/docker-entrypoint-initdb.d/1-schema.sql \
  postgres:16

# Eine eigene Zeile dazu, damit sichtbar wird, was überlebt
docker container exec meine-db psql -U kurs -d helloworld \
  -c "INSERT INTO gruss (text) VALUES ('Hallo aus dem Volume')"

# Die Probe: löschen, neu erzeugen, wieder abfragen
docker container stop meine-db && docker container rm meine-db

docker container run -d \
  --name meine-db \
  -p 5432:5432 \
  -e POSTGRES_DB=helloworld \
  -e POSTGRES_USER=kurs \
  -e POSTGRES_PASSWORD=geheim \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v kurs-daten:/var/lib/postgresql/data \
  -v "$(pwd)/schema.sql":/docker-entrypoint-initdb.d/1-schema.sql \
  postgres:16

docker container exec meine-db psql -U kurs -d helloworld -c "SELECT * FROM gruss"
```

Vier Zeilen kommen zurück, nicht drei und nicht sechs: Die eigene Zeile ist noch
da, und `schema.sql` ist **nicht** ein zweites Mal gelaufen.

**`meine-db` bleibt am Ende stehen** – die nächste Übung spricht mit ihr.

## Optional: das Passwort aus einer Datei

```bash
echo 'geheim' > passwort.txt

docker container stop meine-db && docker container rm meine-db
docker volume rm kurs-daten && docker volume create kurs-daten

docker container run -d \
  --name meine-db \
  -p 5432:5432 \
  -e POSTGRES_DB=helloworld \
  -e POSTGRES_USER=kurs \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/db-passwort \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v kurs-daten:/var/lib/postgresql/data \
  -v "$(pwd)/passwort.txt":/run/secrets/db-passwort \
  -v "$(pwd)/schema.sql":/docker-entrypoint-initdb.d/1-schema.sql \
  postgres:16

docker container logs meine-db          # ... database system is ready to accept connections
```

Dass der Container **läuft**, ist der Nachweis: Ohne Passwort – auf welchem Weg
auch immer – bricht er ab wie im ersten Schritt. Der Zeilenumbruch aus `echo`
stört nicht, das Image schneidet ihn ab.

**Das frische Volume ist nötig.** Auf einem bereits eingerichteten
Datenverzeichnis greift ein geändertes Passwort nicht – das Image richtet nur
ein, was fehlt.

`passwort.txt` liegt bewusst **nicht** in diesem Repository. Auf einer
Betriebsplattform legt diese Datei ohnehin nicht der Mensch an, sondern die
Secrets-Verwaltung der Plattform.

## Worauf es in der Nachbesprechung ankommt

1. **Nichts davon hat das Image angefasst.** Dasselbe Artefakt, vier verschiedene
   Ausprägungen – das ist der Satz der Einheit.
2. **Die Logs sind der erste Griff**, nicht die letzte Rettung. Schritt 1 ist
   genau dafür da.
3. **Das Schema ist eine Datei, kein Befehl.** Sie läuft beim ersten Start, und
   nur dann. Wer das Schema später vermisst, hatte ein nicht leeres
   Datenverzeichnis.
4. **Der dritte Eimer bekommt sein Werkzeug:** Zustand gehört in ein Volume. Die
   offene Rechnung aus Block 1 ist damit beglichen.

## Antworten auf die Reflexionsfragen

1. **Woher weißt Du, welche Umgebungsvariablen ein Image auswertet?** Aus seinem
   Datenblatt – hier dem [Eintrag auf Docker Hub](https://hub.docker.com/_/postgres).
   Technisch erzwungen ist das nirgends, und genau das ist die Schwachstelle: Ein
   Tippfehler fällt **nicht** auf. Mit `POSTGRES_DATABASE` statt `POSTGRES_DB`
   startet der Container klaglos, legt die Standarddatenbank `kurs` an – und erst
   die erste Abfrage auf `helloworld` geht ins Leere.
2. **Wo liegen die Daten jetzt, und wem gehören sie?** In einem von Docker
   verwalteten Ablageort auf dem Host, unabhängig vom Container; `docker volume ls`
   zeigt ihn. Ohne Volume lägen sie in der Schreibschicht des Containers und wären
   mit ihm weg – genau das war in Block 1 beim Löschen zu sehen.
3. **Wo landen die Log-Ausgaben?** Auf `stdout` des Containers, abrufbar mit
   `docker container logs`. Eine Logdatei läge **im** Container: Wer sie lesen
   will, muss hinein, und beim Löschen ist sie weg. Über `stdout` sammelt die
   Plattform die Ausgabe ein, ohne die Anwendung zu kennen – deshalb ist es keine
   Notlösung, sondern die Schnittstelle.
4. **Warum ist `POSTGRES_PASSWORD_FILE` besser als `POSTGRES_PASSWORD`?** Weil der
   Wert dann nur noch an einer Stelle steht. Als Umgebungsvariable steht er im
   Befehl, in der Shell-History, in `docker container inspect`, in der
   Prozessliste und in jedem CI-Protokoll, das den Befehl mitschreibt – und er
   wird an jeden Prozess im Container weitervererbt. Als Datei ist er eine
   einzelne Stelle mit eigenen Zugriffsrechten, die auf einer Plattform nicht der
   Mensch einhängt, sondern deren Secrets-Verwaltung. Weg ist das Geheimnis damit
   nicht; es ist nur nicht mehr überall.

## Die Dateien dazu

### [`schema.sql`](schema.sql)

Wird beim **ersten** Start nach `/docker-entrypoint-initdb.d/` eingehängt.

```sql
CREATE TABLE gruss (
  id   SERIAL PRIMARY KEY,
  text TEXT NOT NULL
);

INSERT INTO gruss (text)
VALUES ('Hallo Welt'), ('Hello World'), ('Bonjour le monde');
```
