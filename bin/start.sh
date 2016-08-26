#!/bin/bash

echo "Starting Bastion ..."

trap '' INT TSTP 0 1 2 5 15

SID=$RANDOM

tmux new-session -d -s bastion-$SID
tmux send-keys -t bastion-$SID "exec python -B ../run.py $SID $1" C-m
tmux attach -t bastion-$SID

