# Lösung · Die Webanwendung spricht mit der Datenbank

Zwei Container in einem eigenen Netzwerk: Die Anwendung findet ihre Datenbank
über deren **Namen**, und die Zugangsdaten kommen von außen.

Zur Übung:
[Die Webanwendung spricht mit der Datenbank](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/anwendung-und-datenbank/issue.html)

`app.py` und `requirements.txt` liegen hier zum Kopieren. Es ist eine **neue**
Anwendung – wer die aus `anwendungen-im-container/` behalten will, legt diese
daneben.

## Die Befehle in der Reihenfolge

```bash
# GIT BASH UNTER WINDOWS: Jedem Befehl, der ein Verzeichnis einhängt, ein
# MSYS_NO_PATHCONV=1 voranstellen.

# 1. Das Netzwerk
docker network create helloworld-network
docker network ls

# 2. Die Datenbank neu erzeugen – diesmal im Netzwerk. Das Volume bleibt,
#    also auch die Tabelle gruss.
docker container rm -f meine-db

docker container run -d \
  --name meine-db \
  --network helloworld-network \
  -p 5432:5432 \
  -e POSTGRES_DB=helloworld \
  -e POSTGRES_USER=kurs \
  -e POSTGRES_PASSWORD=geheim \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v kurs-daten:/var/lib/postgresql/data \
  postgres:16

docker container exec meine-db psql -U kurs -d helloworld -c "SELECT * FROM gruss"

# 3. Die Anwendung: dasselbe Netzwerk, die Zugangsdaten als Umgebungsvariablen
docker container run --rm \
  --network helloworld-network \
  -p 8080:8080 \
  -v "$(pwd)":/app -w /app \
  -e DB_HOST=meine-db \
  -e DB_NAME=helloworld \
  -e DB_USER=kurs \
  -e DB_PASSWORD=geheim \
  python:3.12-slim \
  sh -c "pip install -r requirements.txt && python app.py"

curl http://localhost:8080

# 4. Die Probe aufs Exempel: Datenbank weg
docker container stop meine-db
curl http://localhost:8080          # scheitert
docker container start meine-db
curl http://localhost:8080          # geht wieder
```

**Die Anwendung läuft im Vordergrund** – wie in der vorigen Übung. Die Aufrufe ab
`curl` gehören deshalb in eine **zweite Shell**. Wer lieber eine einzige Shell
behält, startet sie mit `-d --name meine-app` und sieht mit
`docker container logs -f meine-app` zu.

`DB_PORT` wird nicht gesetzt – der Vorgabewert 5432 stimmt. `DB_HOST` dagegen
**muss** gesetzt werden, und Benutzer und Passwort ebenso: Die Vorgaben im
Quelltext (`localhost`, `postgres`/`postgres`) passen zu keiner Datenbank dieses
Kurses.

## Das Fehlerbild bei gestoppter Datenbank

Nachgemessen, nicht angenommen – im Log der Anwendung steht:

```text
psycopg2.OperationalError: could not translate host name "meine-db" to address:
Name or service not known
```

**Das ist ein Namensproblem, kein Zeitproblem.** Ein gestoppter Container ist aus
dem DNS des Netzwerks verschwunden; der Name zeigt auf nichts mehr. Nach
`docker container start` antwortet die Anwendung wieder, ohne dass sie neu
gestartet werden muss – sie baut ihre Verbindung bei jeder Anfrage neu auf.

Die andere Meldung, `connection refused`, bedeutet das Gegenteil: Der Name wurde
aufgelöst, aber auf der Gegenseite nimmt noch niemand an. Das ist der Fall, wenn
die Datenbank gerade erst startet.

## Worauf es in der Nachbesprechung ankommt

1. **`meine-db` statt `localhost`.** `localhost` ist im Container die Anwendung
   selbst. Den Namen der Datenbank löst der DNS des Netzwerks auf – deshalb
   braucht es das eigene Netzwerk.
2. **Ein laufender Container wechselt das Netzwerk nicht.** Deshalb wird die
   Datenbank neu erzeugt, und deshalb ist das Volume Gold wert: Die Daten bleiben.
3. **Im Quelltext stehen nur Vorgabewerte.** Dasselbe Image läuft damit gegen
   jede Datenbank – das ist die Einheit von gestern, jetzt an einer zweiten
   Anwendung.
4. **Die Meldungen auseinanderhalten** (siehe oben). Wer das kann, debuggt
   Netzwerkprobleme in Containern selbst.

## Antworten auf die Reflexionsfragen

1. **Warum funktioniert `meine-db`, und warum wäre `localhost` falsch?** Jeder
   Container hat seinen eigenen Netzwerk-Namensraum: `localhost` ist im Container
   der Anwendung die Anwendung selbst, dort lauscht keine Datenbank. In einem
   benutzerdefinierten Netzwerk betreibt Docker einen DNS, der jeden Container
   unter seinem Namen führt – `meine-db` wird dort aufgelöst. Im
   Standard-Bridge-Netzwerk gäbe es diese Auflösung nicht; dann bliebe nur die
   IP-Adresse, und die ändert sich bei jedem Neuerzeugen.
2. **Welche Angaben kommen von außen?** `DB_HOST`, `DB_NAME`, `DB_USER`,
   `DB_PASSWORD` – und `DB_PORT`, wenn er abweicht. Im Quelltext stehen nur
   Vorgabewerte, damit die Anwendung auf dem eigenen Rechner ohne Zutun startet.
   Echte Werte gehören dort nicht hin: Sie unterscheiden sich je Umgebung, und das
   Passwort hätte im Quelltext ohnehin nichts verloren.
3. **Was ist passiert, als die Datenbank weg war?** Der Aufruf endete mit einem
   Fehler (siehe oben), die Anwendung selbst lief weiter. Nach dem Start der
   Datenbank antwortete sie wieder. **Wünschenswert ist genau das:** Eine
   Anwendung soll einen fehlenden Dienst überstehen und es erneut versuchen,
   statt sich zu beenden – auf einer Plattform ist ein kurz nicht erreichbarer
   Dienst der Normalfall, nicht die Ausnahme.
