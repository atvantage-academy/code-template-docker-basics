CREATE TABLE gruss (
  id   SERIAL PRIMARY KEY,
  text TEXT NOT NULL
);

INSERT INTO gruss (text)
VALUES ('Hallo Welt'), ('Hello World'), ('Bonjour le monde');
