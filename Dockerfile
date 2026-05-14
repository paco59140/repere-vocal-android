FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV COMPANION_DATA_DIR=/data

WORKDIR /app

COPY cloud_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cloud_api/app ./app

RUN mkdir -p /data

EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
