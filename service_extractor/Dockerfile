FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /service_extractor
WORKDIR /service_extractor
COPY . /service_extractor
COPY requirements.txt /service_extractor
RUN apt-get update -qq && apt-get -y install ffmpeg
RUN pip install -r requirements.txt
# Для извлечения волн из аудио
#RUN apt-get install audiowaveform
#RUN apt-get install git make cmake gcc g++ libmad0-dev libid3tag0-dev libsndfile1-dev libgd-dev libboost-filesystem-dev libboost-program-options-dev libboost-regex-dev

# Команда для извлечения
#audiowaveform -i test_en.mp3 -o test.json -z 256 -b 8