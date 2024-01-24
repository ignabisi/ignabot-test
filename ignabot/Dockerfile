# pull official base image
FROM python:3.11.2-slim-buster

# set working directory
WORKDIR /usr/src/app

# set environment variables

# Prevents Python from writing pyc files to disc (prevents caching issues)
ENV PYTHONDONTWRITEBYTECODE 1

# Ensures that Python outputs are sent straight to terminal (keeps Docker logs clean)
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get -y install netcat gcc \
    && apt-get clean

# install python dependencies
RUN pip install --no-cache --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .