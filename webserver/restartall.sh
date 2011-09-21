#!/bin/bash
/etc/init.d/apache2 restart
pkill hookbox
pkill python
./runall.sh
