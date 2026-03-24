FROM python:3.12-slim
COPY import.py /app/import.py
COPY workflows/ /app/workflows/
WORKDIR /app

RUN useradd -r -s /bin/false appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "import.py"]
