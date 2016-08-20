#!/bin/bash

echo "Starting Bastion ..."

tmux new-session -d -s bastion
tmux send-keys -t bastion 'python ../bastion.py' C-m
tmux attach -t bastion

