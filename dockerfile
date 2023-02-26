FROM python:3.11.0-slim-buster

WORKDIR /

COPY / /

RUN pip install -r requirements.txt
CMD python src/main.py
