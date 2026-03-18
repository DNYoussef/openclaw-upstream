FROM python:3.12-slim

RUN pip install --no-cache-dir psycopg2-binary

COPY router.py /app/router.py
WORKDIR /app

CMD ["python", "router.py"]
