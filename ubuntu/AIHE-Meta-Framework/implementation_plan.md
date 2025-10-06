# Architektur- und Implementierungsplan: AIHE Meta-Framework

## 1. Zielsetzung

Dieses Dokument beschreibt die technische Architektur und den Implementierungsplan für die Entwicklung der AIHE Meta-Framework Applikation gemäß der "Vollständigen Technischen Spezifikation v2.0 Enhanced".

## 2. Technologiestack

Um eine moderne, skalierbare und wartbare Applikation zu gewährleisten, wird folgender Technologiestack gewählt:

| Komponente | Technologie | Begründung |
| :--- | :--- | :--- |
| **Backend-Framework** | **FastAPI (Python)** | Hochperformantes, asynchrones Web-Framework, ideal für die Erstellung von REST-APIs. Die Python-Basis erleichtert die Implementierung der komplexen mathematischen Berechnungslogik. Die automatische API-Dokumentation (Swagger UI) beschleunigt die Entwicklung und das Testing. |
| **Datenbank** | **PostgreSQL** | Leistungsstarkes, objektrelationales Datenbanksystem, das für komplexe Datenmodelle und Geschäftslogik bestens geeignet ist. Bietet hohe Stabilität, Skalierbarkeit und Datenintegrität. |
| **Frontend-Framework** | **React (mit TypeScript)** | Führendes Framework zur Erstellung von dynamischen und interaktiven Benutzeroberflächen. Die komponentenbasierte Architektur fördert die Wiederverwendbarkeit und Wartbarkeit. TypeScript sorgt für Typsicherheit und verbessert die Codequalität. |
| **Datenvisualisierung** | **D3.js / Chart.js** | Leistungsstarke Bibliotheken zur Erstellung der in der Spezifikation geforderten interaktiven Diagramme, Heatmaps und Dashboards. |
| **Deployment** | **Docker & Docker Compose** | Containerisierung der Applikation zur Sicherstellung einer konsistenten Entwicklungsumgebung und zur Vereinfachung des Deployments in eine Produktionsumgebung. |
| **Testing** | **Pytest (Backend), Jest/React Testing Library (Frontend)** | Etablierte Frameworks für Unit-, Integrations- und End-to-End-Tests zur Sicherstellung der Codequalität und der Einhaltung der Spezifikationen. |
| **CI/CD** | **GitHub Actions** | Automatisierung von Tests, Builds und Deployments direkt aus dem GitHub-Repository heraus. |

## 3. Projektstruktur

Das Projekt wird in einem Monorepo organisiert, um die Verwaltung von Backend und Frontend zu vereinfachen. Die Verzeichnisstruktur wird wie folgt aussehen:

```
/AIHE-Meta-Framework
├── backend/                # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API Endpunkte (Routen)
│   │   ├── core/           # Kernlogik, Berechnungen, Engines
│   │   ├── crud/           # Datenbank-Operationen (Create, Read, Update, Delete)
│   │   ├── models/         # Datenbank-Modelle (SQLAlchemy)
│   │   ├── schemas/        # Pydantic-Schemata für API-Validierung
│   │   └── main.py         # Applikations-Startpunkt
│   ├── tests/
│   └── Dockerfile
├── frontend/               # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── assets/         # Bilder, CSS, etc.
│   │   ├── components/     # Wiederverwendbare UI-Komponenten
│   │   ├── features/       # Feature-basierte Module (Assessments, Reports, etc.)
│   │   ├── hooks/          # Custom React Hooks
│   │   ├── services/       # API-Client
│   │   ├── types/          # TypeScript-Typdefinitionen
│   │   └── App.tsx         # Haupt-Applikationskomponente
│   └── Dockerfile
├── docs/                   # Dokumentation
├── .github/                # GitHub Actions Workflows
├── docker-compose.yml      # Docker Compose Konfiguration
└── README.md               # Projekt-Dokumentation
```

## 4. Implementierungs-Roadmap

Die Entwicklung wird in logische Phasen unterteilt, die auf den Phasen des Hauptplans aufbauen.

### Phase 5: Core Framework Komponenten implementieren
- **Task 5.1:** Projektstruktur gemäß Plan anlegen.
- **Task 5.2:** Docker-Konfiguration für Backend und Frontend erstellen.
- **Task 5.3:** Datenbank-Modelle in `backend/app/models/` basierend auf dem Datenmodell der Spezifikation implementieren.
- **Task 5.4:** Pydantic-Schemata in `backend/app/schemas/` für die API-Datenvalidierung erstellen.
- **Task 5.5:** CRUD-Operationen in `backend/app/crud/` für die Kern-Entitäten implementieren.

### Phase 6: API und Backend Services entwickeln
- **Task 6.1:** API-Endpunkte in `backend/app/api/` für die Kern-Entitäten (Organisation, Assessment) erstellen.
- **Task 6.2:** Berechnungslogik für die 5 Kernmetriken (EQI, RGI, SI, SBS, Kontextscore) in `backend/app/core/` implementieren.
- **Task 6.3:** Logik für die dynamische Gewichtung und die Archetype Engine entwickeln.
- **Task 6.4:** API-Endpunkte für die erweiterten Module (Lernloop, Speed-to-Impact) erstellen.

### Phase 7: Frontend Interface und UI Komponenten erstellen
- **Task 7.1:** Basis-Layout und Navigationsstruktur gemäß UI/UX-Spezifikation in React umsetzen.
- **Task 7.2:** Service-Schicht für die Kommunikation mit dem Backend-API erstellen.
- **Task 7.3:** UI-Komponenten für die Erstellung und Verwaltung von Assessments entwickeln.
- **Task 7.4:** Dashboards und Visualisierungen für die Reporting-Engine mit D3.js/Chart.js implementieren.
- **Task 7.5:** UI für die erweiterten Module (Lernloop, Action Kits etc.) erstellen.

### Phase 8: Testing, Qualitätssicherung und Dokumentation
- **Task 8.1:** Unit- und Integrationstests für das Backend (Pytest) schreiben.
- **Task 8.2:** Unit- und Komponententests für das Frontend (Jest/RTL) schreiben.
- **Task 8.3:** End-to-End-Tests für die kritischen User Journeys einrichten.
- **Task 8.4:** CI/CD-Pipeline mit GitHub Actions für automatisierte Tests und Builds konfigurieren.
- **Task 8.5:** API-Dokumentation vervollständigen und eine umfassende `README.md` erstellen.

### Phase 9: Deployment-Konfiguration und Produktionsreife
- **Task 9.1:** Produktionsreife Docker-Images für Backend und Frontend erstellen.
- **Task 9.2:** `docker-compose.yml` für die Produktionsumgebung anpassen (z.B. mit Nginx als Reverse Proxy).
- **Task 9.3:** Logging, Monitoring und Error-Tracking für die Produktionsumgebung konfigurieren.
- **Task 9.4:** Datenbank-Migrationsstrategie (z.B. mit Alembic) implementieren.

## 5. Nächste Schritte

Die nächste Phase ist die Implementierung der Core Framework Komponenten, beginnend mit der Erstellung der Projektstruktur und der Docker-Konfiguration.

