FROM python:3.11-slim-buster

WORKDIR /

COPY / /

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
CMD python src/main.py
