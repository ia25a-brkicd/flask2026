# flask template 🌶️

Dieses Projekt dient einen Einstiegspunkt für die Entwicklung einer [flask](https://flask.palletsprojects.com/en/) Applikation.\
Das README erkl&auml;rt auch gewisse Python-Basics 🐍\
Das folgende Projekt funktioniert nicht auf dem EAP. Es muss am privaten Laptop gearbeitet werden.

## Was ist flask

Flask ist ein in Python geschriebenes Webframework.
Sein Fokus liegt auf Erweiterbarkeit und guter Dokumentation.
©️ Wikipedia

## Vorbereitungen

Stelle sicher das du die neuste Python Version installiert hast (3.14.x)
-> https://www.python.org/downloads/

Nutze oder installiere VSCode
-> https://code.visualstudio.com/download

## venv (Virtual Environment)

### Was ist eine virtuelle Umgebung?

Eine venv ist für vieles zuständig.
Momentan ist es vereinfacht gesagt wie maven.
Es wird dazu genutzt, um Bibliotheken (z.B. flask) zu installieren für ein spezifisches Projekt.

### Virtuelle Umgebung erstellen

Im Projektordner:

```command
python -3 -m venv .venv
```

### Virtuelle Umgebung verwenden

Super, du hast eine venv erstellt, das bringt dir allerdings noch nichts.
Um die venv korrekt zu verwenden, musst du sie noch aktivieren:

```command
cd venv/Scripts
./activate
```

Nun kannst du Bibliotheken installieren und verwenden.

### Arbeiten mit einer venv

Um Bibliotheken zu speichern musst du ins root Verzeichnis deines Projektes (z.B. C:\workarea\localGitRepo\flask)
Hier findest du ein requirements.txt (Das ist im Prinzip, ähnlich wie das pom.xml in einem maven-Projekt).

Um die Bibiliotheken zu verwenden, musst du die Abhängigkeiten installieren (venv zuerst aktivieren!)

```command
pip install -r requirements.txt
```

Wenn du nun eine neue Abhängigkeit installierst kannst du diese speichern mit 

```command
pip freeze > requirements.txt
```

## Web Applikation starten

Um die WebApplikation zu starten musst du die Abhängigkeiten installieren (siehe Kapitel oben) und aschliessend das main.py ausführen.

```command
python main.py
```

## Weitere Infos

* [flask](https://confluence.prod.zkb.ch/display/AE/Flask)
* [flask](https://www.geeksforgeeks.org/flask-rendering-templates/)
* [venv](https://medium.com/analytics-vidhya/virtual-environments-in-python-186cbd4a1b94)
