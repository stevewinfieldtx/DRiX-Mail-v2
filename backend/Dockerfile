FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app app
COPY migrations migrations
CMD ["sh","-c","python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
