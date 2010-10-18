#!/bin/bash

export LD_LIBRARY_PATH=fmodapi/lib:$LD_LIBRARY_PATH
python ./test.py
