# AIHE Meta-Framework

Ein ganzheitliches Bewertungs- und Steuerungsinstrument für die verantwortungsvolle Integration von Künstlicher Intelligenz in Organisationen.

## Überblick

Das AIHE (AI Ethics) Meta-Framework ist eine produktionsreife Webanwendung, die Organisationen dabei unterstützt, ihre KI-Reife zu bewerten und systematisch zu verbessern. Das Framework basiert auf 8 Dimensionen und 16 Subdimensionen und bietet erweiterte Funktionen wie dynamische Gewichtung, iterative Lernschleifen und intelligente Maßnahmenempfehlungen.

## Kernfunktionen

### 🎯 Assessment-Engine
- **8 Dimensionen, 16 Subdimensionen**: Strukturierte Bewertung der KI-Reife
- **4-stufiges Reifegradmodell**: Initial, Emerging, Integrated, Transformative
- **Dynamische Gewichtung**: Kontextabhängige Anpassung der Bewertungskriterien

### 📊 Metriken & Analytics
- **EQI (Equilibrium Quality Index)**: Misst die Ausgewogenheit der Entwicklung
- **RGI (Reifegrad-Index)**: Gewichteter Gesamtreifegrad
- **SI (Spannungsindex)**: Identifiziert kritische Ungleichgewichte
- **SBS (System Balance Score)**: Strategischer Gesamtwert
- **Kontextscore**: Berücksichtigt organisatorische Komplexität

### 🔄 Erweiterte Module
- **Lernloop**: 5-Phasen-Zyklus für kontinuierliche Verbesserung
- **Speed-to-Impact**: Priorisierung von Maßnahmen nach Wirkung und Aufwand
- **Archetype Engine**: Organisationsprofile für personalisierte Empfehlungen
- **Quick Scan**: 2-Stunden-Schnellbewertung
- **Compliance Cockpit**: Mapping zu regulatorischen Frameworks
- **Action Kits**: Bibliothek vordefinierter Maßnahmenpakete

## Technologie-Stack

| Komponente | Technologie | Version |
|------------|-------------|---------|
| **Backend** | FastAPI | 0.104.1 |
| **Datenbank** | PostgreSQL | 15 |
| **Frontend** | React + TypeScript | 18+ |
| **Containerisierung** | Docker & Docker Compose | Latest |
| **API-Dokumentation** | Swagger UI / ReDoc | Auto-generiert |

## Schnellstart

### Voraussetzungen
- Docker und Docker Compose
- Git

### Installation

1. **Repository klonen**
   ```bash
   git clone https://github.com/aigambitkg/AIHE-Meta-Framework.git
   cd AIHE-Meta-Framework
   ```

2. **Anwendung starten**
   ```bash
   docker-compose up -d
   ```

3. **Services überprüfen**
   - Backend API: http://localhost:8000
   - API Dokumentation: http://localhost:8000/docs
   - Frontend: http://localhost:3000 (nach Implementierung)
   - Datenbank: localhost:5432

### Erste Schritte

1. **API testen**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Organisation erstellen**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/organisations/" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "Beispiel GmbH",
          "organisation_type": "KMU",
          "industry": "Technologie",
          "country": "DE"
        }'
   ```

## Projektstruktur

```
AIHE-Meta-Framework/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API Endpunkte
│   │   ├── core/              # Kernlogik & Konfiguration
│   │   ├── crud/              # Datenbank-Operationen
│   │   ├── models/            # SQLAlchemy Modelle
│   │   └── schemas/           # Pydantic Schemata
│   ├── tests/                 # Backend Tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React Frontend (geplant)
├── docs/                      # Dokumentation
├── .github/                   # CI/CD Workflows
├── docker-compose.yml         # Docker Compose Konfiguration
└── README.md
```

## Entwicklung

### Backend-Entwicklung

1. **Virtuelle Umgebung erstellen**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oder
   venv\Scripts\activate     # Windows
   ```

2. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

3. **Entwicklungsserver starten**
   ```bash
   uvicorn app.main:app --reload
   ```

### Tests ausführen

```bash
cd backend
pytest
```

## API-Dokumentation

Die vollständige API-Dokumentation ist verfügbar unter:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Wichtige Endpunkte

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/organisations/` | GET | Liste aller Organisationen |
| `/api/v1/organisations/` | POST | Neue Organisation erstellen |
| `/api/v1/organisations/{id}` | GET | Organisation abrufen |
| `/api/v1/organisations/{id}` | PUT | Organisation aktualisieren |
| `/api/v1/assessments/` | GET | Liste aller Assessments |
| `/api/v1/dimensions/` | GET | Alle Dimensionen abrufen |

## Datenmodell

Das Framework basiert auf folgenden Hauptentitäten:

- **Organisation**: Zentrale Entität mit Klassifizierung und Archetyp
- **Assessment**: Bewertungsinstanz mit Zeitraum und Status
- **Dimension/Subdimension**: 8+16 Bewertungsdimensionen (Stammdaten)
- **Scores**: Ist/Soll-Bewertungen pro Subdimension
- **Context Factors**: Kontextuelle Einflussfaktoren

## Roadmap

### ✅ Phase 1: Core Framework (Aktuell)
- [x] Backend-Architektur und API
- [x] Datenmodell und CRUD-Operationen
- [x] Docker-Konfiguration
- [x] Basis-Dokumentation

### 🚧 Phase 2: Berechnungslogik (In Arbeit)
- [ ] Implementierung der 5 Kernmetriken
- [ ] Dynamische Gewichtungs-Engine
- [ ] Spannungsanalyse zwischen Dimensionen

### 📋 Phase 3: Frontend & UX
- [ ] React-Frontend mit TypeScript
- [ ] Interaktive Dashboards und Visualisierungen
- [ ] Assessment-Wizard und User Journeys

### 🔄 Phase 4: Erweiterte Module
- [ ] Lernloop-Implementierung
- [ ] Speed-to-Impact Priorisierung
- [ ] Action Kits System
- [ ] Compliance Cockpit

### 🚀 Phase 5: Produktionsreife
- [ ] Umfassende Tests und QA
- [ ] Performance-Optimierung
- [ ] Deployment-Automatisierung
- [ ] Monitoring und Logging

## Beitragen

Wir freuen uns über Beiträge! Bitte lesen Sie unsere [Contribution Guidelines](CONTRIBUTING.md) für Details zum Entwicklungsprozess.

### Entwicklungsrichtlinien

1. **Code-Qualität**: Befolgen Sie PEP 8 für Python und ESLint-Regeln für TypeScript
2. **Tests**: Schreiben Sie Tests für neue Funktionen
3. **Dokumentation**: Aktualisieren Sie die Dokumentation bei API-Änderungen
4. **Commits**: Verwenden Sie aussagekräftige Commit-Nachrichten

## Lizenz

Dieses Projekt steht unter der [Apache License 2.0](LICENSE).

## Support

- **Dokumentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/aigambitkg/AIHE-Meta-Framework/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/aigambitkg/AIHE-Meta-Framework/discussions)

---

**AIHE Meta-Framework** - Verantwortungsvolle KI-Integration für moderne Organisationen.
