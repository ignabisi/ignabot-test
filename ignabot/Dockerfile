FROM python:3.11.2-slim-buster

# set working dir
WORKDIR /usr/src/app

# Prevents Python from writing pyc files to disc (prevents caching issues)
ENV PYTHONDONTWRITEBYTECODE 1

# Ensures that Python outputs are sent straight to terminal (keeps Docker logs clean)
ENV PYTHONUNBUFFERED 1


RUN apt-get update \
    && apt-get -y install netcat gcc \
    && apt-get clean
    
# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install python dependencies
RUN pip install --no-cache --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add ignabot
COPY . .