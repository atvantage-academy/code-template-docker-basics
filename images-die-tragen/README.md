# Lösung · Ein Dockerfile gegen die Praxis prüfen

Ein absichtlich schlechtes Dockerfile, die Befunde dazu und eine überarbeitete
Fassung. **Die Übung ist ein Review** – es geht ums Beurteilen, nicht ums Bauen.

Zur Übung:
[Ein Dockerfile gegen die Praxis prüfen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/images-die-tragen/issue.html)

Der Baustein steht außerhalb der Tagesplanung; er wird eingesetzt, wenn Zeit
bleibt, oder einzeln.

## Die Befundliste zum Ausgangs-Dockerfile

Es sind sieben – vier zu finden ist das Ziel, mehr ist Zugabe.

| Zeile | Befund | Folge im Betrieb |
| --- | --- | --- |
| `FROM debian:latest` | kein fester Tag | Derselbe Build ergibt in einem halben Jahr ein anderes Image. |
| `FROM debian:…` + `apt-get install nginx` | Betriebssystem plus Handarbeit statt eines fertigen NGINX-Images | Größer, langsamer, und die Pflege des Servers liegt bei Dir. |
| `curl git build-essential` | Bauwerkzeuge im Laufzeit-Image | Nichts davon wird im Betrieb gebraucht; jedes Paket ist Angriffsfläche. |
| drei getrennte `RUN`-Zeilen | jede legt eine Schicht an | Das `rm` in Zeile 4 macht das Image **nicht** kleiner – die Listen stecken in der Schicht darunter. |
| `COPY . /usr/share/nginx/html/` | kopiert **alles**, auch das Dockerfile | Was im Bau-Kontext liegt, landet im Image – auch Dateien, die dort nichts zu suchen haben. |
| kein `USER` | der Prozess läuft als `root` | Wer aus der Anwendung ausbricht, ist root im Container. Nachgemessen: `whoami` sagt `root`. |
| `CMD nginx -g "daemon off;"` | Shell-Form statt Exec-Form | Der Befehl läuft über `/bin/sh -c`. Ob danach noch eine Shell zwischen Docker und dem Prozess steht, hängt von der Shell ab – die Exec-Form (`["nginx", …]`) nimmt diese Unsicherheit heraus und übergibt die Argumente, wie sie dastehen. |

## Die Messung

```bash
docker image build -t review:schlecht .
docker image build -f Dockerfile.gut -t review:gut .
docker image ls review
```

| Image | Größe |
| --- | --- |
| `review:schlecht` | **612 MB** |
| `review:gut` | **49,7 MB** |

**Der größte Anteil kommt aus dem Basis-Image**, nicht aus dem Aufräumen: Ein
schlankes NGINX-Image auf Alpine statt eines vollen Debian mit nachinstalliertem
Server. Die Bauwerkzeuge sind der zweite Posten.

## Non-Root geht nicht nachträglich

Der naheliegende Eingriff – `USER nginx` vor das offizielle `nginx`-Image – **funktioniert
nicht.** Nachgemessen:

```text
nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)
```

Der Server braucht Schreibrechte in `/var/cache/nginx`, und die hat der Benutzer
`nginx` dort nicht. Deshalb steht in der Lösung `nginxinc/nginx-unprivileged` –
ein Image, das für den Betrieb ohne `root` gebaut ist und deshalb auf **8080**
lauscht.

```bash
docker container run -d --name review-gut -p 8090:8080 review:gut
curl http://localhost:8090
docker container exec review-gut whoami      # nginx
```

Zum Vergleich im Ausgangs-Image: `whoami` sagt `root`.

**Das ist die Lektion hinter dem Befund:** Non-Root ist keine Zeile, die man
anhängt – es muss im Image vorgesehen sein.

### Nachgemessen: die Shell-Form ist hier harmloser als ihr Ruf

Die übliche Begründung lautet, der Prozess laufe als Kind einer Shell und bekomme
keine Signale. **Für dieses Beispiel stimmt das nicht:** Sowohl `dash` (Debian)
als auch `ash` (Alpine) ersetzen sich bei einem einzelnen Befehl selbst, PID 1
war in beiden Fassungen `nginx`, und `docker container stop` kehrte jeweils
sofort zurück.

Der Befund bleibt trotzdem richtig – nur mit der ehrlichen Begründung: Die
Exec-Form hängt nicht vom Verhalten einer Shell ab und gibt die Argumente
unverändert weiter. *Wer es im Kurs als Signalproblem erklärt, sollte es vorher
einmal nachgemessen haben.*

## Worauf es in der Nachbesprechung ankommt

1. **Das zweite Augenpaar ist der Inhalt.** Nicht die vollständige Liste zählt,
   sondern die Erfahrung, dass jemand anderes etwas findet. Genau das ist die
   Begründung für Reviews an Dockerfiles – die in der Praxis fast nie
   stattfinden.
2. **Die Zahl nennen lassen**, nicht vorsagen. 612 gegen 50 überzeugt, „schlanke
   Basis-Images sind besser“ nicht.
3. **Der Scan ist ein Anfang, kein Ergebnis.** Was er nicht findet, ist die
   wichtigere Hälfte.
4. **Das Image altert ohne Zutun.** Der Satz, der hängen bleiben soll.

## Antworten auf die Reflexionsfragen

1. **Welchen Befund hat nur eine von beiden gefunden?** Keine Musterlösung – die
   Erfahrung ist die Antwort. Erfahrungsgemäß werden `latest` und die Größe
   zuerst gesehen, die Form von `CMD` und das zu weite `COPY` zuletzt.
2. **Wie viel kleiner, und woher?** 612 MB → 49,7 MB. Der größte Anteil kommt aus
   dem Basis-Image, der zweitgrößte aus den Bauwerkzeugen.
3. **Warum macht das Löschen in einer eigenen Zeile das Image nicht kleiner?**
   Weil jede `RUN`-Zeile eine Schicht anlegt und keine Schicht je wieder
   schrumpft. Die Paketlisten stecken in der Schicht darunter; die vierte Zeile
   legt nur eine weitere Schicht darüber, in der sie fehlen. Im Ergebnis trägt das
   Image beides.
4. **Was ändert Non-Root, und warum genügt keine `USER`-Zeile am Ende?** Wer aus
   der Anwendung ausbricht, hat weniger Rechte; manche Plattformen starten einen
   Container als `root` gar nicht erst. Nachträglich geht es nicht – siehe oben:
   Das Image muss dafür gebaut sein.
5. **Warum ein Image ohne Codeänderung neu bauen?** Weil seine Bestandteile
   altern. Im Basis-Image und in den Paketen werden Schwachstellen bekannt und
   behoben; ein Neubau zieht die Korrekturen mit. **Das Image wird schlechter,
   ohne dass sich etwas ändert.**
6. **Was findet ein Scan nicht?** Fehler im eigenen Code, Konfigurationsfehler –
   und ob eine gemeldete Schwachstelle im konkreten Fall überhaupt erreichbar
   ist. Er sagt, was drin ist, nicht, was davon zählt.

## Die Dateien dazu

### [`Dockerfile`](Dockerfile)

Das Ausgangsmaterial – **absichtlich schlecht**, nicht als Vorlage verwenden.

```dockerfile
# ABSICHTLICH SCHLECHT – das Ausgangsmaterial der Übung.
FROM debian:latest
RUN apt-get update
RUN apt-get install -y nginx curl git build-essential
RUN rm -rf /var/lib/apt/lists/*
COPY . /usr/share/nginx/html/
EXPOSE 80
CMD nginx -g "daemon off;"
```

### [`Dockerfile.gut`](Dockerfile.gut)

```dockerfile
# Erste Stufe: alles, was nur zur Aufbereitung gebraucht wird.
FROM debian:12-slim AS aufbereitung
WORKDIR /arbeit
COPY index.html .
RUN echo "<p>gebaut in der Aufbereitungsstufe</p>" >> index.html

# Zweite Stufe: ein Image, das für den Betrieb ohne root gebaut ist.
# Es lauscht deshalb auf 8080, nicht auf 80.
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=aufbereitung /arbeit/index.html /usr/share/nginx/html/index.html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

### [`index.html`](index.html)

```html
<h1>Review</h1>
```
