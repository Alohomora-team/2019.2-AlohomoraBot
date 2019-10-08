FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/lib/python3.7/site-packages

WORKDIR /home

COPY docker/bot/requirements.txt .

RUN apk add --update --no-cache \
        libressl-dev \
        musl-dev \
        libffi-dev \
        g++ \
        gcc \
        py3-numpy \
        py3-scipy \
        ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ .

CMD python3 main.py
