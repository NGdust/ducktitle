FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /auth
WORKDIR /auth
COPY . /auth
COPY requirements.txt /auth
RUN pip install -r requirements.txt