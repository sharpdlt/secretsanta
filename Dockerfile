FROM python:3.9-slim as app

WORKDIR /app/

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PYTHONPATH=/app

COPY ./app ./app

COPY ./alembic.ini /app/