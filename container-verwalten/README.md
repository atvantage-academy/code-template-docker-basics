# Lösung · Container verwalten

Ein fremdes Image holen, einen Container daraus betreiben – und am **zweiten**
Container sehen, was nicht im Image steckt.

Zur Übung:
[Einen Container aus einem fremden Image betreiben](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/container-verwalten/issue.html)

## Die Befehle in der Reihenfolge

```bash
# Zwei Stände desselben Images holen: einmal ohne Tag, einmal mit
docker image pull nginx
docker image pull nginx:1.27.5

# Nachsehen, was lokal liegt – die Spalte TAG beachten
docker image ls

# Container erzeugen, zunächst OHNE Tür nach außen
docker container create --name mein-webserver nginx:1.27.5

# Erzeugte, noch nicht gestartete Container sieht man nur mit -a
docker container ls -a

docker container start mein-webserver

# Von INNEN antwortet der Server – er läuft also, er ist nur nicht erreichbar
docker container exec mein-webserver curl -s http://localhost

# Die Port-Weitergabe gehört zur ERZEUGUNG: löschen und neu
docker container stop mein-webserver
docker container rm mein-webserver
docker container create --name mein-webserver -p 8080:80 nginx:1.27.5
docker container start mein-webserver
curl http://localhost:8080

# Eine Datei IM laufenden Container anlegen
docker container exec mein-webserver bash -c "echo 'Hallo Welt' > /usr/share/nginx/html/hallo.html"
curl http://localhost:8080/hallo.html

# Stoppen und starten: die Datei ist noch da
docker container stop mein-webserver
docker container start mein-webserver
curl http://localhost:8080/hallo.html

# Der zweite Container aus DEMSELBEN Image: anderer Name, anderer Port außen
docker container create --name zweiter-webserver -p 8081:80 nginx:1.27.5
docker container start zweiter-webserver
docker container ls

curl http://localhost:8080/hallo.html   # 200 – die eigene Seite
curl http://localhost:8081/hallo.html   # 404 – das Image kennt sie nicht
curl http://localhost:8081              # 200 – die Startseite von NGINX

# Aufräumen
docker container stop mein-webserver zweiter-webserver
docker container rm mein-webserver zweiter-webserver
```

## Der letzte Schritt steht absichtlich ohne Befehl in der Übung

Zwei Dinge müssen am zweiten Container anders sein, und beide meldet Docker
deutlich, wenn man sie übersieht:

| Abgeschrieben | Meldung |
| --- | --- |
| derselbe Name | `Conflict. The container name "/mein-webserver" is already in use` |
| derselbe Port außen (`-p 8080:80`) | `Bind for 0.0.0.0:8080 failed: port is already allocated` |

**Innen bleibt 80.** Der Webserver im Container weiß nichts davon, dass er von
außen unter 8081 zu erreichen ist – die Weitergabe macht der Host.

## Worauf es in der Nachbesprechung ankommt

1. **Ohne `-p` keine Tür nach außen** – und nachträglich nicht zu ändern, weil
   die Weitergabe zur Erzeugung des Containers gehört. Dass der Server trotzdem
   läuft, zeigt der Aufruf von innen.
2. **Was im Container entsteht, gehört nicht ins Image.** Der zweite Container
   liefert `hallo.html` nicht aus, obwohl er aus derselben Vorlage kommt. Dafür
   muss nichts gelöscht werden – der Vergleich genügt.
3. `docker container run --rm` fasst `create` + `start` (+ `pull`) zusammen und
   räumt den Container am Ende weg.

## Antworten auf die Reflexionsfragen

1. **Woran lag es, dass der erste Container nicht erreichbar war?** Es fehlte die
   Port-Weitergabe. Der Server lauschte im Container auf 80, aber nichts reichte
   eine Anfrage von außen hinein.
2. **Was ist mit `hallo.html` passiert – und was wäre beim Löschen?** Nach
   `stop`/`start` ist sie noch da: Es ist derselbe Container. Beim Löschen und
   Neuerzeugen wäre sie weg, denn der neue Container entsteht aus dem Image – und
   das kennt die Datei nicht. Genau das zeigt auch der zweite Container.
3. **`docker container run --rm -it nginx:1.27.5 /bin/sh`?** Erzeugt und startet
   in einem Schritt, hängt ein Terminal an (`-it`) und löscht den Container beim
   Verlassen (`--rm`). Nützlich, um schnell in ein Image hineinzusehen, ohne
   etwas zu hinterlassen.
4. **Bedeutung von `latest`?** Kein Versionsname, sondern ein beweglicher Zeiger:
   Wer ohne Tag zieht, bekommt ihn – und morgen unter Umständen ein anderes
   Image. Für etwas, das verlässlich laufen soll, gehört ein fester Tag hin.
5. **Was bedeutet „Aliases“ in der Dokumentation?** Derselbe Befehl unter einem
   kürzeren Namen: `docker pull` ist ein Alias für `docker image pull`. In diesem
   Kurs gilt die Langform – sie nennt, worauf der Befehl wirkt.
