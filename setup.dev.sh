#!/bin/bash

# Выполнить команду:
# Если добавить аргумент - экспортируются только переменные окружения
#
# . setup.dev.sh
# или
# source setup.dev.sh
#


# Переменные окружения
export $(echo `grep --regexp ^[A-Za-z] .env | cut -d ' ' -f1`)
unset DEBUG


if [ $# -eq 0 ]
then
    # Директория с общими модулями (файлами)
    pwd=`pwd`
    modules=`echo ${pwd}/common_modules/`

    # Массив общих модулей
    # Одна строка - одно правило.
    # Записывать через пробел. Первое значение - общий модуль.
    # Остальные знаения - сервисы, куда добавляется жесткая ссылка на модуль (в modules/)
    declare -a files=(
        "filebase.py service_download_video service_editor service_extractor service_video"
        "wsSendler.py service_download_video service_editor service_extractor service_recognize"
        "probe.py service_download_video service_video"
        "downloader.py service_download_video service_video"
        "logger.py service_download_video service_extractor service_recognize service_video service_websocket"
        "sentry_sdk.py service_download_video service_editor service_extractor service_recognize service_video service_websocket"

    )

    # Добавление жестких ссылок на общие файлы (с заменой файла)
    len_files=${#files[@]}
    for (( i=0; i<len_files; i++ ));
    do
        IFS=' ' read -r -a array <<< "${files[i]}"
        len=${#array[@]}
        link="${modules}${array[0]}"
        for (( j=1; j<len; j++ ));
        do
            out_link="${pwd}/${array[$j]}/modules/${array[0]}"
            dir=`dirname ${out_link}`
            if [[ ! -e $dir ]]; then `mkdir $dir`; fi
    #        echo "ln -f ${link} ${out_link}"
            `ln -f ${link} ${out_link}`
        done
    done
fi