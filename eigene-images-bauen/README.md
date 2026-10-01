# Lösung · Ein eigenes Image bauen

Die eigene Seite wandert ins Image: Was bisher von außen eingehängt wurde, ist
jetzt Teil des Artefakts und lässt sich weitergeben, ohne zu erklären, wie man es
installiert.

Zur Übung:
[Ein eigenes Image bauen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/eigene-images-bauen/issue.html)

Die `index.html` ist dieselbe wie in `container-verwalten/` – dort hat der
Container sie noch eingehängt bekommen.

## Die Befehle in der Reihenfolge

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

## Was ein Bau ohne `-t` hinterlässt

Nachgemessen mit Docker 29.8.0: Das Image taucht in `docker image ls`
**gar nicht** auf. Zu finden ist es erst mit
`docker image ls --filter dangling=true`, und dort heißt es `<untagged>`.
Ältere Fassungen listen es in `docker image ls` als `<none>:<none>`.

In beiden Fällen gilt dasselbe: Das Image ist fertig und über seine ID nutzbar,
aber niemand findet es wieder. Wer dreimal ohne `-t` baut, hat drei davon – das
sind die *dangling images*.

## Worauf es in der Nachbesprechung ankommt

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

## Antworten auf die Reflexionsfragen

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

## Die Dateien dazu

### [`Dockerfile`](Dockerfile)

```dockerfile
FROM nginx:1.27.5
COPY index.html /usr/share/nginx/html/index.html
RUN echo "<h1>Beim Bauen entstanden</h1>" > /usr/share/nginx/html/gebaut.html
EXPOSE 80
```

### [`index.html`](index.html)

```html
<h1>Diese Seite liegt auf meinem Rechner</h1>
```
