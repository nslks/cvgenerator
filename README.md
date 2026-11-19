# cvgenerator

Lebenslauf als YAML schreiben, fertiges PDF bekommen. So sieht das aus: [`data/example.pdf`](data/example.pdf)

## Warum

- **Inhalt getrennt vom Design:** eine YAML pro Bewerbung, das Layout bleibt immer gleich.
- **ATS-freundlich:** echter Text, keine Silbentrennung, Schlagwörter bleiben ganz.
- **Nichts installieren außer Docker:** Python, LaTeX und Schriften stecken im Image.

## Nur einen CV erzeugen

Du brauchst nur [Docker](https://www.docker.com/products/docker-desktop/).

```bash
mkdir mein-cv && cd mein-cv
curl -fsSLo cv.yaml https://raw.githubusercontent.com/nslks/cvgenerator/main/data/example.yaml
# cv.yaml mit deinen Daten füllen (photo: auf dein Foto zeigen lassen oder löschen)
docker run --rm -v "$PWD:/work" ghcr.io/nslks/cvgenerator build --data cv.yaml --template single
```

Das PDF liegt danach in `output/cv-single.pdf`.

## Selbst anpassen

Auf GitHub **„Use this template“** klicken und das Repo **privat** anlegen. Bei einem öffentlichen Fork wären deine Daten sichtbar, sobald du sie committest.

```bash
git clone <dein-repo> && cd cvgenerator
cp data/example.yaml data/cv.yaml
docker compose run --rm cv build --template single
```

| Was ändern | Wo |
| --- | --- |
| Inhalt | `data/cv.yaml` |
| Design | `templates/single/cv.tex.j2` |
| Neues Design | `templates/<name>/` anlegen, kommt als `output/cv-<name>.pdf` raus |

Templates und Code werden in den Container gemountet, Änderungen wirken also beim nächsten Lauf. Neu bauen musst du das Image nur, wenn du das `Dockerfile` änderst:

```bash
docker build -t ghcr.io/nslks/cvgenerator .
```

Alles unter `data/` außer dem Beispiel ist per `.gitignore` ausgeschlossen.

## Mit einem KI-Agenten

Am einfachsten: Repo öffnen, deinem Agenten (z. B. Claude Code) dieses README zeigen und sagen, was du willst. Den Rest macht er.

**Tipp für den richtig guten Workflow:** Lass dir vom Agenten einen Skill schreiben, dem du nur noch eine Stellenanzeige schickst:

1. Anzeige lesen und mit deiner `cv.yaml` abgleichen
2. Gap-Analyse: Was passt, was fehlt, was sollte stärker rein
3. Konkrete Vorschläge, wie der CV angepasst wird, und auf dein OK warten
4. Nach deinem OK: PDF bauen und als `output/<stellenanzeige>/cv.pdf` ablegen

So hast du pro Bewerbung einen eigenen Ordner mit einem passgenauen CV.

## Optionen

```bash
--data data/cv-en.yaml   # andere Datei (language: en für englische Überschriften)
--template single        # nur dieses Template statt aller
--suffix firma-stelle    # ergibt output/cv-single-firma-stelle.pdf
--no-pdf                 # nur .tex erzeugen
```

## Templates

Damit Jinja nicht mit LaTeX kollidiert: `\VAR{ ... }` für Werte, `\BLOCK{ ... }` für Logik, `%%` für Zeilenbefehle. Jeder Text muss durch den Filter `tex`, der LaTeX-Sonderzeichen escaped.

Tests: `uv run pytest`
