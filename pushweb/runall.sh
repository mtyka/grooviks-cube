 #!/bin/bash

 ./authapp.py &
hookbox -d -r bakonv8 -p 2974 --cbhost=127.0.0.1 --cbport=8080 --cbpath= &
sleep 1
cd ../pacsci
./groovikhookbox.py
#./random_colors.py &
#open http://localhost:8080
