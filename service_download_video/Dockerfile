FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /service_download_video
WORKDIR /service_download_video
COPY . /service_download_video
COPY requirements.txt /service_download_video
RUN apt-get update -qq && apt-get -y install ffmpeg
RUN pip install -r requirements.txt