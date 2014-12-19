#!/bin/bash
nohup python runscallion.py &
echo "Writing PID to scallion.pid file"
echo $! > scallion.pid