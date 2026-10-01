# ABSICHTLICH SCHLECHT – das Ausgangsmaterial der Übung.
FROM debian:latest
RUN apt-get update
RUN apt-get install -y nginx curl git build-essential
RUN rm -rf /var/lib/apt/lists/*
COPY . /usr/share/nginx/html/
EXPOSE 80
CMD nginx -g "daemon off;"
