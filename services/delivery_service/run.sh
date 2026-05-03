#! /bin/bash

# echo $1
PORT=$1 python manage.py runserver 0.0.0.0:$1 --noreload
