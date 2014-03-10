#!/bin/bash

echo "Starting django server"
sleep 2
cd webserver 
python manage.py runserver 0.0.0.0:80 --noreload &> /home/cube/django.log &

echo "Starting hookbox server"
sleep 2
hookbox -d -r bakonv8 -a lair2low -p 2974 --cbhost=127.0.0.1 --cbport=80 &> /home/cube/hookbox.log &

echo "Starting controller processs"
sleep 2
cd ../controller
./groovikhookbox.py &> /home/cube/groovikhookbox.log &

sleep 2
echo "/* ----- Groovik's Cube Running With Processes ----- */"
ps aux | grep python