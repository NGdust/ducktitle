FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /service_recognize
WORKDIR /service_recognize
COPY . /service_recognize
COPY requirements.txt /service_recognize
RUN pip install -r requirements.txt