FROM python:3.12-slim

RUN pip install --no-cache-dir psycopg2-binary

COPY app.py /app/app.py
WORKDIR /app

RUN useradd -r -s /bin/false appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8090/health', timeout=3)" || exit 1

CMD ["python", "app.py"]
