# Zakat360

Plateforme Flask pour calculer la Zakat, gérer des causes, créer des dons, exporter des rapports et administrer le contenu.

## Fonctionnalités
- Calculateur de Zakat (base or/argent) avec prix des métaux et arrondis `Decimal`.
- Tableau de bord avec KPI et graphique mensuel (Chart.js).
- Dons avec preuve (validation stricte mimetype et extension).
- Export annuel en CSV et PDF (ReportLab).
- Authentification (local + Google OAuth), export JSON du compte, suppression de compte.
- Espace Admin (CRUD causes, mise à jour des statuts de dons) avec audit log.
- Cache prix des métaux (DB, 6h) + fallback local.
- Planificateur quotidien (APScheduler) pour créer des dons en attente pour utilisateurs Pro.
- Migrations Alembic via Flask-Migrate.
- Tests (unitaires + intégration) avec `pytest`.

## Prérequis
- Python 3.12+
- SQLite (par défaut) ou PostgreSQL en production

## Installation
1. Cloner le projet et entrer dans le dossier.
2. Créer un environnement virtuel et installer les dépendances:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copier `.env.example` vers `.env` et renseigner les valeurs (clé secrète, DB, Metals API, OAuth Google si nécessaire).

## Lancer l’application
```bash
set FLASK_APP=wsgi.py
python wsgi.py  # mode dev
```
Ou via `gunicorn`:
```bash
gunicorn wsgi:app
```

## Base de données et migrations
Initialiser et appliquer les migrations:
```bash
flask db init
flask db migrate -m "init"
flask db upgrade
```

Pour données de démo:
```bash
python init_data.py
```

## Tests
Exécuter tous les tests:
```bash
pytest -q
```

## Configuration (env)
Variables principales dans `.env`:
- `FLASK_ENV`, `SECRET_KEY`
- `DATABASE_URL` (ex: `sqlite:///zakat360_dev.db`)
- `UPLOAD_DIR`
- `METALS_API_URL`, `METALS_API_KEY`, `FX_RATE_MAD`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_DISCOVERY_URL`

## Notes sécurité
- Cookies de session sécurisés activés selon l’environnement.
- Content Security Policy (CSP) restrictif (auto + CDNs nécessaires).
- Validation stricte des fichiers uploadés (extensions et MIME) et taille max.

## Déploiement
- Le `Procfile` inclut `web: gunicorn wsgi:app`.
- Pour PostgreSQL, configurer `DATABASE_URL` et exécuter les migrations.