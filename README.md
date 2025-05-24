# Airflow + dbt Training

This repository contains training materials for a hands-on session covering Airflow and dbt. It includes:

- Presentation decks in Markdown format
- Automated generation of PDF and PowerPoint files using Marp CLI
- A local Docker-based Airflow environment for running the exercises

## Contents

- `presentation/` — All slide decks (`.md`) and related assets (images, diagrams)
- `airflow-local/` — Docker environment for running Airflow and PostgreSQL locally
- `.github/workflows/` — GitHub Actions configuration to build slides automatically

## Slide Generation Workflow

Slide decks are written in Markdown and converted automatically to:

- PDF (`.pdf`)
- PowerPoint (`.pptx`)

These are generated in the `presentation/dist/` directory using Marp CLI via GitHub Actions.

### How it works

On every push to the repository:

1. All `presentation/*.md` files are processed
2. Corresponding `.pdf` and `.pptx` files are created
3. Output is saved to `presentation/dist/`
4. The artifacts are available for download via the GitHub Actions run

## Local Airflow Environment

The `airflow-local/` folder contains a `docker-compose.yml` configuration for spinning up the training environment locally.

### Requirements

- Docker
- Docker Compose

### Usage

```bash
cd airflow-local
docker-compose up
```

This will start:

- Airflow webserver and scheduler
- PostgreSQL database (used by both Airflow and dbt)

The Airflow web UI will be available at:

http://localhost:8080

Default login (unless overridden in `docker-compose.yml`):

- Username: `airflow`
- Password: `airflow`

You can add your DAGs to the `airflow-local/dags/` directory and see them appear in the UI.

## Exercises

Each part of the training corresponds to a section in the slide deck and includes:

- Writing basic DAGs using dummy and Python operators
- Ingesting data using custom functions
- Modeling and testing using dbt from inside the Airflow container
- Generating a simple output chart from transformed data

## License

MIT
