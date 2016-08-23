#!/bin/bash

echo "Starting Bastion ..."

SID=$RANDOM

tmux new-session -d -s bastion-$SID
tmux send-keys -t bastion-$SID "python -B ../run.py $SID $1" C-m
tmux attach -t bastion-$SID

