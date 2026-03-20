FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir camel-oasis psycopg2-binary

COPY app.py /app/app.py
COPY archetypes/ /app/archetypes/
WORKDIR /app

VOLUME ["/tmp/mirofish-traces"]

RUN useradd -r -s /bin/false appuser && chown -R appuser:appuser /app /tmp/mirofish-traces
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health', timeout=3)" || exit 1

CMD ["python", "app.py"]
