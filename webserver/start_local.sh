./manage.py runserver 0.0.0.0:8080 &
hookbox -d -r bakonv8 -p 2974 --cbhost=127.0.0.1 --cbport=8080 &

echo 'Now go to ../controller and start groovikhookbox.py then navigate to http://localhost:8080/cube_multimode?position=1&grey=0'
