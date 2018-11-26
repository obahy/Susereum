#!/bin/bash
api=$1
path=$2
repoid=$3
echo "python3 ../Sawtooth/bin/code_smell.py default --url http://127.0.0.1:$api --path $path --repo $repoid"
echo 'practicum2018' | sudo -S python3 ../Sawtooth/bin/code_smell.py default --url http://127.0.0.1:$api --path $path --repo $repoid