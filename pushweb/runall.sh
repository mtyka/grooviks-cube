 #!/bin/bash

 ./authapp.py &
sleep 2
hookbox -d -r bakonv8 -a lair2low -p 2974 --cbhost=127.0.0.1 --cbport=8080 --cbpath= &
sleep 2
cd ../pacsci
./groovikhookbox.py &
#./random_colors.py &
open http://localhost:8080

sleep 2
echo "You'll need to go to ../pacsci and run groovikhookbox.py"
echo "It never successfully starts by itself. Go figure."
