#!/bin/bash

# Выполнить команду:
# Если добавить аргумент - экспортируются только переменные окружения
#
# . setup.prod.sh
# или
# source setup.prod.sh
#

source setup.dev.sh
export DEBUG=TRUE
docker-compose up ${@:1}