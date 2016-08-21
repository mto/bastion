#!/bin/bash

echo "Starting Bastion ..."

SID=$RANDOM

tmux new-session -d -s bastion-$SID
tmux send-keys -t bastion-$SID "python ../run.py $SID" C-m
tmux attach -t bastion-$SID

