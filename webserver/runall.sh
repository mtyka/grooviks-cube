 #!/bin/bash

echo "Starting django server"
./manage.py runserver 0.0.0.0:8080 &> django.log &
sleep 2

echo "Starting hookbox server"
hookbox -d -r bakonv8 -a lair2low -p 2974 --cbhost=127.0.0.1 --cbport=8080 &> hookbox.log &
sleep 2
cd ../controller

echo "Starting controller processs"
./groovikhookbox.py &> groovikhookbox.log &

sleep 2
echo "You'll likely need to go to ../pacsci and run groovikhookbox.py"
echo "It rarely successfully starts by itself. Go figure."
