FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir camel-oasis psycopg2-binary

COPY app.py /app/app.py
COPY archetypes/ /app/archetypes/
WORKDIR /app

VOLUME ["/tmp/mirofish-traces"]

CMD ["python", "app.py"]
