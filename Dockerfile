FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN poetry install --no-root

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 