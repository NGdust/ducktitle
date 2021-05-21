FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /service_editor
WORKDIR /service_editor
COPY . /service_editor
COPY requirements.txt /service_editor
RUN apt-get update -qq && apt-get -y install ffmpeg
RUN pip install -r requirements.txt