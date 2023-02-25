FROM python:3.11-slim-buster

WORKDIR /

COPY bot.py .
COPY main.py .
COPY poetry.lock .
COPY pyproject.toml .
COPY summarize.py .

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
CMD python main.py
