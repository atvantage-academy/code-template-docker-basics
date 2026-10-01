---
layout: default
title: "Musterlösungen · Docker-Grundlagen"
---

Hier stehen die **Musterlösungen** zu den Übungen der Schulung
„Docker-Grundlagen“ der ATVANTAGE Academy. Die Übungen selbst stehen in den
[Lernenden-Unterlagen](https://atvantage-academy.github.io/training-material-container-technologies/docker-grundlagen/).

**Sieh hier erst nach, wenn Du es selbst versucht hast.** Der Wert einer Übung
liegt im Suchen, nicht im Ergebnis – und im Kurs wird nach dem Weg gefragt, nicht
nach der Lösung.

## Die Lösungen

{% assign loesungen = site.pages | where: "kategorie", "loesung" | sort: "reihenfolge" %}
<ul class="loesungen">
{% for loesung in loesungen %}
  <li>
    <a href="{{ loesung.url | relative_url }}">{{ loesung.title }}</a>
    {% if loesung.beschreibung %}<p>{{ loesung.beschreibung }}</p>{% endif %}
  </li>
{% endfor %}
</ul>

## Was hier nicht liegt

Zugangsdaten, Registry-Konten, kundenspezifische Adressen. Die Passwörter in den
Beispielen (`geheim`) sind Kursmaterial und ausdrücklich keine Empfehlung.

## Der Anwendungscode wird gestellt, nicht geschrieben

Die Lernenden programmieren in diesem Kurs nicht. Der Code steht vollständig in
der jeweiligen Übungsbeschreibung; er liegt hier zum Kopieren – und damit der
Trainer ihn schnell zur Hand hat, etwa um ihn vorab in ein Image zu backen, wenn
die Umgebung kein `pip install` zulässt.
