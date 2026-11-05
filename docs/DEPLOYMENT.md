# Deployment auf Render

Die App besteht auf Render aus drei Teilen, die `render.yaml` im Hauptordner gemeinsam anlegt:

| Teil | Name | Art |
| --- | --- | --- |
| Datenbank | `lerntool-db` | PostgreSQL, Tarif „free“ |
| Backend | `lerntool-api` | Web-Service (Python, gunicorn) |
| Frontend | `lerntool` | Statische Seite (Vite-Build) |

## Was du vorher brauchst

1. Ein Konto bei [render.com](https://render.com) (Anmeldung mit GitHub ist am einfachsten).
2. Dein GitHub-Repository `NicoMeyerDev/Lerntool` mit dem Branch, der die Datei `render.yaml` enthält (nach dem Merge: `main`).
3. Einen Benutzernamen und ein langes Passwort für deinen Zugang zur App (empfohlen mindestens 12 Zeichen, nur für diese App verwenden; zu kurze oder häufige Passwörter lehnt der Start ab).

## Variablen im Überblick

| Variable | Wer setzt sie | Bedeutung |
| --- | --- | --- |
| `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_DEBUG`, `DJANGO_HTTPS_ERZWINGEN`, `PYTHON_VERSION` | `render.yaml` | automatisch, nichts zu tun |
| `LERNTOOL_BENUTZER`, `LERNTOOL_PASSWORT` | du, beim Apply | dein Zugang zur App |
| `DJANGO_CORS_ORIGINS` | du, nach dem ersten Start | Adresse des Frontends |
| `VITE_API_URL` | du, nach dem ersten Start | Adresse des Backends |

## Schritt für Schritt

1. In Render: **New → Blueprint**, Repository `Lerntool` wählen, Branch `main`.
2. Render liest `render.yaml` und fragt nach drei Werten (die übrigen setzt Render selbst):
   - `LERNTOOL_BENUTZER`: dein Benutzername,
   - `LERNTOOL_PASSWORT`: dein Passwort,
   - `DJANGO_CORS_ORIGINS` und `VITE_API_URL`: beim ersten Mal **leer lassen oder `https://platzhalter.invalid` eintragen**, die echten Adressen kennst du erst nach dem ersten Start.
3. **Apply** klicken und warten, bis alle drei Teile „Live“ zeigen.
4. Adressen notieren (stehen oben im jeweiligen Dienst), zum Beispiel:
   - Backend: `https://lerntool-api.onrender.com`
   - Frontend: `https://lerntool.onrender.com`
   (Ist der Name schon vergeben, hängt Render eine Endung an. Nimm dann die echte Adresse.)
5. Im Dienst `lerntool-api` unter **Environment**: `DJANGO_CORS_ORIGINS` = Adresse des Frontends. Speichern, das Backend startet neu.
6. Im Dienst `lerntool` unter **Environment**: `VITE_API_URL` = Adresse des Backends. Speichern und unter **Manual Deploy → Deploy latest commit** neu bauen (die Adresse wird beim Bauen eingebaut).
7. Frontend-Adresse im Browser öffnen, mit deinem Benutzer anmelden. Der Systemstatus unten auf der Startseite muss grün sein.

## Was beim Start des Backends passiert

`python manage.py migrate` legt die Tabellen an, `import_inhalte` lädt die Lerninhalte, `anlegen_nutzer` legt deinen Zugang an (nur wenn noch kein Nutzer existiert, ein vorhandenes Passwort wird nie überschrieben). Danach startet gunicorn. Das Passwort ändern: in Render `LERNTOOL_PASSWORT` ändern reicht **nicht**, weil der Nutzer schon existiert. Dafür braucht es einen Shell-Zugang (kostenpflichtiger Tarif) oder eine neu angelegte Datenbank.

## Grenzen des kostenlosen Tarifs (Stand Render-Doku)

- Das Backend schläft nach 15 Minuten ohne Aufruf ein und braucht beim nächsten Aufruf etwa eine Minute zum Aufwachen.
- Die kostenlose Datenbank **läuft 30 Tage nach dem Anlegen ab** (dann 14 Tage Gnadenfrist zum Upgrade, danach werden die Daten gelöscht). Dein Lernfortschritt liegt dort. Für dauerhaften Betrieb muss die Datenbank auf einen bezahlten Tarif.
- Es gibt keinen Shell-Zugang und keine Backups.
- Prüfe vor dem Klick auf „Apply“ die aktuellen Preise und Grenzen unter <https://render.com/docs/free>.

## Hinweise zur Sicherheit

- `DJANGO_SECRET_KEY` erzeugt Render zufällig, `DJANGO_DEBUG` ist `False`, HTTPS wird erzwungen.
- `python manage.py check --deploy` meldet zwei bewusst nicht gesetzte HSTS-Optionen (`INCLUDE_SUBDOMAINS`, `PRELOAD`): `onrender.com` gehört nicht dir, deshalb wären sie unpassend.
- **Login-Bremse:** Die App begrenzt Anmeldeversuche auf 10 pro Minute und Client. Hinter dem Render-Proxy ist die Client-Erkennung nicht belegt (die Render-Doku nennt die Zahl der Proxys nicht), und die Zähler gelten pro gunicorn-Prozess. Die Bremse ist hier deshalb nur eine Zusatzhürde. Der Schutz kommt aus einem langen, einmaligen Passwort. Siehe `docs/OFFEN.md`.
- Passwort und Schlüssel stehen nur im Render-Dashboard, nie im Repository.

## Quellen

- Blueprint-Format: <https://render.com/docs/blueprint-spec>
- Kostenloser Tarif: <https://render.com/docs/free>
- Django-Checkliste für den Betrieb: <https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/>
