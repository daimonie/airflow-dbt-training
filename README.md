# Airflow + dbt Training

This repository contains training materials for a hands-on session covering Airflow and dbt. It includes:

- Presentation decks in Markdown format
- Automated generation of PDF and PowerPoint files using Marp CLI
- A local Docker-based Airflow environment for running the exercises

## Installation
For following this training, the following installation is recommended:
- Download Docker desktop
- Open powershell (`win+r`, type `powershell`, `enter`)
- run `wsl --install ubuntu`
- run `wsl --setdefault ubuntu`
- run `wsl`, set a username and pass you remember
- check current user (e.g. `cd ~` and `pwd`). If root, `su` to user
- Make sure of docker permission by using `sudo usermod -aG docker $USER`
- refresh shell `newgrp docker`
- run `cd ~ && git clone https://github.com/daimonie/airflow-dbt-training` if public
- then `cd airflow-dbt-training/airflow-local`
- `docker compose up`
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

### Components

The environment includes:
- Airflow webserver and scheduler (Apache Airflow 2.8.1)
- PostgreSQL database for Airflow metadata
- Separate PostgreSQL database for data warehousing (DWH)

### Usage

```bash
cd airflow-local
docker-compose up
```

The Airflow web UI will be available at:

http://localhost:8080

Default login credentials:
- Username: `admin`
- Password: `admin`

### Available DAGs

The `airflow-local/dags/` directory includes several example DAGs demonstrating different Airflow features:

## License

All rights reserved. This repository and its contents are proprietary.  
You may not reproduce, distribute, or adapt this material without written permission from the author.  
Any proceeds or benefits resulting from a license violation must be remitted in full to the author.
