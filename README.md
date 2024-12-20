# Nexus API

A FastAPI-based API for document ingestion and similarity search.

## Setup

1. Install Poetry (package manager):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Run the application:
```bash
poetry run uvicorn app.main:app --reload
```

## API Documentation

Once running, visit http://localhost:8000/docs for the interactive API documentation.

## Development

- Format code: `poetry run black .`
- Sort imports: `poetry run isort .`
- Run linter: `poetry run flake8`
- Run tests: `poetry run pytest`
```

You can now delete the requirements.txt file. To get started:

1. Install Poetry following the instructions above
2. Run `poetry install` to create a virtual environment and install all dependencies
3. Use `poetry add package-name` to add new dependencies
4. Use `poetry add -D package-name` to add development dependencies

Poetry will manage your virtual environment automatically and keep track of exact versions in the poetry.lock file, ensuring reproducible builds across different environments.