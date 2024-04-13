FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app/ /app/app
COPY alembic.ini /app
COPY alembic/ /app/alembic
COPY html/ /app/html

CMD alembic upgrade head && uvicorn app.main:app --port 8000 --host 0.0.0.0
