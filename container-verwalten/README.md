# Lösung · Container verwalten

Drei Container aus demselben Image: einer leer, einer mit einer Seite **darin**,
einer mit einer Seite, die **auf dem eigenen Rechner** liegt.

Zur Übung:
[Einen Container aus einem fremden Image betreiben](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/container-verwalten/issue.html)

## Die Befehle in der Reihenfolge

```bash
# GIT BASH UNTER WINDOWS: Jedem Befehl, der ein Verzeichnis einhängt, ein
# MSYS_NO_PATHCONV=1 voranstellen – sonst baut die Shell den Pfad im Container
# zu einem Windows-Pfad um:  MSYS_NO_PATHCONV=1 docker container create ...

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

# Der zweite Container: anderer Name, anderer Port außen
docker container create --name zweiter-webserver -p 8081:80 nginx:1.27.5
docker container start zweiter-webserver
docker container ls

# Die Seite entsteht IM zweiten Container
docker container exec zweiter-webserver bash -c "echo 'Hallo Welt' > /usr/share/nginx/html/hallo.html"

curl http://localhost:8081/hallo.html   # 200 – die eigene Seite
curl http://localhost:8080/hallo.html   # 404 – der erste kennt sie nicht

# Stoppen und starten: dieselbe Ausprägung, die Seite ist noch da
docker container stop zweiter-webserver
docker container start zweiter-webserver
curl http://localhost:8081/hallo.html   # 200

# Der dritte Container: die Seite liegt auf dem Rechner und wird hineingereicht
mkdir website
echo '<h1>Diese Seite liegt auf meinem Rechner</h1>' > website/index.html

docker container create --name dritter-webserver -p 8082:80 \
  -v "$(pwd)/website":/usr/share/nginx/html nginx:1.27.5
docker container start dritter-webserver
curl http://localhost:8082

# Ändern – ohne den Container anzufassen
echo '<h1>Geändert, ohne Neustart</h1>' > website/index.html
curl http://localhost:8082                # sofort die neue Fassung

# Aufräumen
docker container stop mein-webserver zweiter-webserver dritter-webserver
docker container rm mein-webserver zweiter-webserver dritter-webserver
```

## Der zweite Container steht absichtlich ohne Befehl in der Übung

Zwei Dinge müssen anders sein, und beide meldet Docker deutlich, wenn man sie
übersieht:

| Abgeschrieben | Meldung |
| --- | --- |
| derselbe Name | `Conflict. The container name "/mein-webserver" is already in use` |
| derselbe Port außen (`-p 8080:80`) | `Bind for 0.0.0.0:8080 failed: port is already allocated` |

**Innen bleibt 80.** Der Webserver im Container weiß nichts davon, dass er von
außen unter 8081 zu erreichen ist – die Weitergabe macht der Host.

## Warum das VERZEICHNIS eingehängt wird und nicht die Datei

Nachgemessen, nicht angenommen: Hängt man die einzelne Datei ein
(`-v "$(pwd)/hallo.html":/usr/share/nginx/html/hallo.html`), liefert NGINX nach
dem nächsten Speichern **404**. Viele Editoren schreiben beim Speichern eine neue
Datei und benennen sie um; der Container hält aber die alte fest. Mit dem
eingehängten **Verzeichnis** wirkt jede Änderung sofort – auch die aus einem
Editor.

## Worauf es in der Nachbesprechung ankommt

1. **Ohne `-p` keine Tür nach außen** – und nachträglich nicht zu ändern, weil
   die Weitergabe zur Erzeugung des Containers gehört. Dass der Server trotzdem
   läuft, zeigt der Aufruf von innen.
2. **Was im Container entsteht, gehört nicht ins Image.** Der erste Container
   liefert `hallo.html` nicht aus, obwohl beide aus derselben Vorlage kommen.
3. **Was hineingereicht wird, liegt draußen** – und bleibt dort, wenn der
   Container weg ist. Das ist der Vorgriff auf „Konfiguration und Zustand“.

## Antworten auf die Reflexionsfragen

1. **Woran lag es, dass der erste Container nicht erreichbar war?** Es fehlte die
   Port-Weitergabe. Der Server lauschte im Container auf 80, aber nichts reichte
   eine Anfrage von außen hinein.
2. **Warum liefert der erste Container `hallo.html` nicht aus?** Weil sie im
   zweiten entstanden ist. Das Image ist der Bauplan und kennt die Datei nicht;
   jeder Container bekommt beim Erzeugen seinen eigenen beschreibbaren Bereich.
   Nach `stop`/`start` ist sie noch da – es ist derselbe Container. Beim Löschen
   und Neuerzeugen wäre sie weg.
3. **Für welche Anwendungsfälle sind Bind Mounts sinnvoll?** Die Seite liegt auf
   dem eigenen Rechner; der Container sieht das Verzeichnis nur an der Stelle, an
   die es eingehängt wurde. Das lohnt sich
   - beim **Entwickeln und Testen** – ändern und sofort sehen, ohne neu zu bauen,
   - um **Konfiguration von außen** hineinzureichen,
   - zum **Austausch von Dateien** zwischen Host und Container,
   - und für Daten, die den Container **überleben** sollen.

   Für den letzten Fall gibt es die zweite Form, das von Docker verwaltete
   **Volume** – das wird in „Konfiguration und Zustand“ selbst gebaut.
4. **`docker container run --rm -it nginx:1.27.5 /bin/sh`?** Erzeugt und startet
   in einem Schritt, hängt ein Terminal an (`-it`) und löscht den Container beim
   Verlassen (`--rm`). Nützlich, um schnell in ein Image hineinzusehen, ohne
   etwas zu hinterlassen.
5. **Bedeutung von `latest`?** Kein Versionsname, sondern ein beweglicher Zeiger:
   Wer ohne Tag zieht, bekommt ihn – und morgen unter Umständen ein anderes
   Image. Für etwas, das verlässlich laufen soll, gehört ein fester Tag hin.
6. **Was bedeutet „Aliases“ in der Dokumentation?** Derselbe Befehl unter einem
   kürzeren Namen: `docker pull` ist ein Alias für `docker image pull`. In diesem
   Kurs gilt die Langform – sie nennt, worauf der Befehl wirkt.
