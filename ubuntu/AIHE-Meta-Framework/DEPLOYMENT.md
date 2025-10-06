# AIHE Meta-Framework Deployment Guide

## Übersicht

Dieses Dokument beschreibt die Deployment-Konfiguration für das AIHE Meta-Framework, eine produktionsreife Anwendung zur Bewertung und Steuerung der verantwortungsvollen Integration von KI in Organisationen.

## Architektur

Das AIHE Meta-Framework besteht aus drei Hauptkomponenten:

- **Backend**: FastAPI-basierte REST API mit PostgreSQL-Datenbank
- **Frontend**: React-basierte Single Page Application (SPA)
- **Datenbank**: PostgreSQL mit vollständiger Schema-Definition

## Systemanforderungen

### Minimale Anforderungen
- **CPU**: 2 vCPUs
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Betriebssystem**: Ubuntu 20.04+ oder vergleichbar

### Empfohlene Produktionsanforderungen
- **CPU**: 4 vCPUs
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **Load Balancer**: Nginx oder ähnlich
- **SSL-Zertifikat**: Let's Encrypt oder kommerziell

## Deployment-Optionen

### Option 1: Docker Compose (Empfohlen für Entwicklung und kleine Deployments)

```bash
# Repository klonen
git clone https://github.com/aigambitkg/AIHE-Meta-Framework.git
cd AIHE-Meta-Framework

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env-Datei entsprechend anpassen

# Services starten
docker-compose up -d

# Datenbank initialisieren
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
```

### Option 2: Kubernetes (Empfohlen für Produktion)

```bash
# Namespace erstellen
kubectl create namespace aihe-framework

# Secrets konfigurieren
kubectl create secret generic aihe-secrets \
  --from-literal=database-url="postgresql://user:password@postgres:5432/aihe_framework" \
  --from-literal=secret-key="your-secret-key" \
  -n aihe-framework

# Deployments anwenden
kubectl apply -f k8s/ -n aihe-framework
```

### Option 3: Manuelle Installation

#### Backend Setup

```bash
# Python-Umgebung vorbereiten
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Datenbank konfigurieren
export DATABASE_URL="postgresql://user:password@localhost:5432/aihe_framework"
export SECRET_KEY="your-secret-key"

# Migrationen ausführen
alembic upgrade head

# Server starten
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Node.js-Abhängigkeiten installieren
cd frontend/aihe-frontend
pnpm install

# Produktions-Build erstellen
pnpm run build

# Mit Nginx oder anderem Webserver bereitstellen
# Build-Ordner: dist/
```

## Umgebungsvariablen

### Backend (.env)

```env
# Datenbank
DATABASE_URL=postgresql://aihe_user:aihe_password@postgres:5432/aihe_framework

# Sicherheit
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

# Logging
LOG_LEVEL=INFO

# Features
ENABLE_DOCS=true
ENABLE_METRICS=true
```

### Frontend (.env.local)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AIHE Meta-Framework
VITE_APP_VERSION=1.0.0
```

## Datenbank-Setup

### PostgreSQL-Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Benutzer und Datenbank erstellen
sudo -u postgres psql
CREATE USER aihe_user WITH PASSWORD 'aihe_password';
CREATE DATABASE aihe_framework OWNER aihe_user;
GRANT ALL PRIVILEGES ON DATABASE aihe_framework TO aihe_user;
\q
```

### Schema-Initialisierung

```bash
# Migrationen ausführen
cd backend
alembic upgrade head

# Stammdaten laden
python -c "
from app.core.database import SessionLocal
from app.models import Dimension, Subdimension
# Stammdaten werden automatisch über init.sql geladen
"
```

## Monitoring und Logging

### Health Checks

Das Framework bietet folgende Health Check-Endpunkte:

- `GET /health` - Allgemeiner Gesundheitsstatus
- `GET /health/db` - Datenbankverbindung
- `GET /health/ready` - Bereitschaftsstatus

### Logging-Konfiguration

```python
# logging.conf
[loggers]
keys=root,aihe

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_aihe]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=app
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('app.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Sicherheit

### SSL/TLS-Konfiguration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Frontend
    location / {
        root /var/www/aihe-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall-Konfiguration

```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## Backup und Recovery

### Datenbank-Backup

```bash
# Automatisches Backup-Skript
#!/bin/bash
BACKUP_DIR="/var/backups/aihe-framework"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/aihe_framework_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U aihe_user aihe_framework > $BACKUP_FILE
gzip $BACKUP_FILE

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Cron-Job für automatische Backups

```bash
# crontab -e
0 2 * * * /path/to/backup-script.sh
```

## Performance-Optimierung

### Datenbank-Indizes

```sql
-- Wichtige Indizes für Performance
CREATE INDEX idx_assessments_organisation_id ON assessments(organisation_id);
CREATE INDEX idx_assessments_created_at ON assessments(created_at);
CREATE INDEX idx_subdimension_scores_assessment_id ON subdimension_scores(assessment_id);
CREATE INDEX idx_context_factors_assessment_id ON context_factors(assessment_id);
```

### Caching-Strategie

```python
# Redis-Konfiguration für Caching
REDIS_URL = "redis://localhost:6379/0"
CACHE_TTL = 3600  # 1 Stunde

# Beispiel für Caching in FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="aihe-cache")
```

## Troubleshooting

### Häufige Probleme

1. **Datenbankverbindungsfehler**
   ```bash
   # Verbindung testen
   psql -h localhost -U aihe_user -d aihe_framework
   ```

2. **CORS-Fehler**
   ```python
   # CORS_ORIGINS in .env überprüfen
   CORS_ORIGINS=http://localhost:3000,https://your-domain.com
   ```

3. **Migration-Fehler**
   ```bash
   # Migrationen zurücksetzen
   alembic downgrade base
   alembic upgrade head
   ```

### Log-Analyse

```bash
# Backend-Logs
docker-compose logs -f backend

# Datenbank-Logs
docker-compose logs -f postgres

# Nginx-Logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Wartung

### Regelmäßige Aufgaben

1. **Wöchentlich**
   - Datenbank-Backups überprüfen
   - Log-Dateien rotieren
   - System-Updates prüfen

2. **Monatlich**
   - Performance-Metriken analysieren
   - Sicherheits-Updates installieren
   - Backup-Recovery testen

3. **Quartalsweise**
   - Vollständige Systemüberprüfung
   - Kapazitätsplanung
   - Disaster Recovery-Test

## Support und Dokumentation

- **API-Dokumentation**: `https://your-domain.com/docs`
- **Technische Spezifikation**: Siehe `docs/technical-specification.pdf`
- **GitHub Repository**: `https://github.com/aigambitkg/AIHE-Meta-Framework`

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE`-Datei für Details.
