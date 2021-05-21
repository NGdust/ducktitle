FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /service_websocket
WORKDIR /service_websocket
COPY . /service_websocket
COPY requirements.txt /service_websocket
RUN pip install -r requirements.txt