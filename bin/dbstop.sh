#!/bin/bash
nohup python run.py &
echo "Writing PID to scallion.pid file"
echo $! > scallion.pid