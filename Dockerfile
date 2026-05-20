# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first to leverage Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app.py ./
COPY templates/ ./templates/
COPY static/ ./static/

# Persistent state (leaderboard.json + flask_session/) lives under /app/data
# so a single volume mount can persist everything mutable.
ENV DATA_DIR=/app/data

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/data/flask_session \
    && chown -R appuser:appuser /app

USER appuser

VOLUME ["/app/data"]

EXPOSE 5000

# Health check hits the index page
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3).status == 200 else 1)"

# Gunicorn serves the Flask `app` object from app.py
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "4", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
