FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /service_video
WORKDIR /service_video
COPY . /service_video
COPY requirements.txt /service_video
RUN apt-get update -qq && apt-get -y install ffmpeg
RUN pip install -r requirements.txt