# Befehle · Container verwalten

Ein fremdes Image holen, einen Container daraus betreiben – und sehen, was beim
Löschen verloren geht.

```bash
# Zwei Stände desselben Images holen: einmal ohne Tag, einmal mit
docker pull nginx
docker pull nginx:1.27.5

# Nachsehen, was lokal liegt – die Spalte TAG beachten
docker images

# Container erzeugen, zunächst OHNE Tür nach außen
docker container create --name mein-webserver nginx:1.27.5

# Erzeugte Container sieht man nur mit -a
docker container ls
docker container ls -a

docker container start mein-webserver

# Schlägt fehl – und das ist der Lerneffekt
curl http://localhost:8080
docker container logs mein-webserver

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

# Löschen und neu erzeugen: die Datei ist weg
docker container stop mein-webserver
docker container rm mein-webserver
docker container create --name mein-webserver -p 8080:80 nginx:1.27.5
docker container start mein-webserver
curl http://localhost:8080/hallo.html

# Aufräumen
docker container stop mein-webserver
docker container rm mein-webserver
```

## Worauf es in der Nachbesprechung ankommt

1. **Ohne `-p` keine Tür nach außen** – und nachträglich nicht zu ändern.
2. **Was im Container entsteht, stirbt mit ihm.** Das Image kennt die Datei nicht.
3. `docker run --rm` fasst `create` + `start` (+ `pull`) zusammen und räumt auf.
