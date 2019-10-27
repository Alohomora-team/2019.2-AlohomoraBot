FROM python:3.7-slim

WORKDIR /home

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/lib/python3.7/site-packages

COPY docker/bot/requirements.txt .

RUN apt-get update && apt-get install -y \
    ffmpeg 
    
COPY docker/bot/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY bot/ .

CMD ["python3", "main.py"]
