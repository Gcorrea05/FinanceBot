FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd --system financebot && useradd --system --gid financebot --home-dir /app financebot

COPY requirements.txt requirements-dev.txt ./

RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

COPY alembic.ini ./
COPY app ./app
COPY migrations ./migrations
COPY scripts ./scripts

RUN mkdir -p /app/data/reports /app/backups/sqlite /app/logs && chown -R financebot:financebot /app

USER financebot

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
