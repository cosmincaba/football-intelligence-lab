# Football Intelligence Lab — Progress Log

## Project Goal

Build an end-to-end football intelligence platform combining **Data Engineering, Analytics, Machine Learning, and AI**.

The project will demonstrate practical skills in Python, SQL, PostgreSQL, Docker, data pipelines, analytics engineering, machine learning, and AI-powered football analysis.

## Phase 1 — Project Foundations

### 1. Repository & Development Environment

- [x] Create public GitHub repository
- [x] Initialize README and Python `.gitignore`
- [x] Clone repository locally
- [x] Create initial folder structure
- [x] Set up Python virtual environment (`.venv`)
- [x] Configure environment variables (`.env` and `.env.example`)
- [x] Protect credentials using `.gitignore`
- [ ] Configure project dependencies and package management

### 2. Database Infrastructure

- [x] Configure PostgreSQL 16 using Docker Compose
- [x] Start and verify PostgreSQL container
- [x] Configure persistent Docker volume
- [x] Connect to PostgreSQL using DBeaver
- [x] Execute SQL queries successfully
- [x] Create `raw` database schema
- [x] Create `raw.matches_json` table
- [x] Define primary key and unique source-file constraint
- [x] Create version-controlled SQL setup script
- [x] Execute SQL script from VS Code terminal

### 3. Data Ingestion

- [x] Identify StatsBomb Open Data as initial data source
- [ ] Complete review of StatsBomb licensing and registration requirements
- [ ] Connect Python to PostgreSQL using `psycopg`
- [ ] Download and parse first football JSON file
- [ ] Calculate SHA-256 content hash
- [ ] Implement idempotent ingestion using PostgreSQL `ON CONFLICT`
- [ ] Implement basic logging and error handling
- [ ] Validate ingestion results in DBeaver

## Development Log

### Day 1 — Project Initialization

**Completed:**
- Created the public GitHub repository.
- Established initial folder structure.
- Created project progress documentation.
- Initialized the Python virtual environment.

**Skills practiced:**
- Git and GitHub
- Repository organization
- Python virtual environments
- Project documentation

### Day 2 — Docker & PostgreSQL Infrastructure

**Completed:**
- Configured PostgreSQL 16 using Docker Compose.
- Created a persistent database volume.
- Configured database credentials using environment variables.
- Successfully connected to PostgreSQL.
- Connected DBeaver to the Docker-hosted database.

**Skills practiced:**
- Docker images vs. containers
- Docker Compose
- Persistent volumes
- Environment variables and credential management
- PostgreSQL connectivity

### Day 3 — Raw Data Layer & Database Design

**Completed:**
- Created the `raw` PostgreSQL schema.
- Created `raw.matches_json` with JSONB payload storage.
- Defined a primary key and unique constraint on `source_file_path`.
- Designed the initial strategy for idempotent ingestion.
- Created and executed a version-controlled SQL setup script.
- Investigated StatsBomb Open Data licensing requirements.

**Key design decisions:**
- Use `source_file_path` to identify each source document.
- Use SHA-256 `content_hash` to detect upstream file changes.
- Preserve one current row per source file in the MVP.
- Use conditional upserts to prevent unnecessary database updates.
- Consider version-history tracking in a future phase.

**Skills practiced:**
- PostgreSQL schemas and DDL
- Primary keys and unique constraints
- JSONB data types
- Database design
- Data ingestion idempotency
- Content hashing concepts
- Reproducible SQL scripts

## Next Steps

1. Complete StatsBomb licence verification.
2. Set up Python dependencies (`psycopg`, `python-dotenv`, `requests`, `pytest`).
3. Build the first Python-to-PostgreSQL connection.
4. Ingest the first StatsBomb JSON document.
5. Test new, unchanged, and updated source-file scenarios.
6. Add automated ingestion tests.

## Skills Practiced

- **Version Control:** Git, GitHub, commits, repository structure
- **Python Development:** Virtual environments, project organization
- **Infrastructure:** Docker, Docker Compose, persistent storage
- **Databases:** PostgreSQL, SQL DDL, constraints, JSONB
- **Data Engineering:** Raw data layers, idempotency, content hashing, ingestion architecture
- **Tools:** VS Code, PowerShell, DBeaver

## Current Status

**Phase 1 — Infrastructure and raw database foundation completed.**

**Next milestone:** First working Python ingestion pipeline — StatsBomb JSON → PostgreSQL.