#!/bin/bash
api=$1
rm smells_exist.txt
if [[ $(sawtooth transaction list --url http://127.0.0.1:$api | grep "code") ]]; then
    touch smells_exist.txt
    echo 'smells found' > smells_exist.txt
else
    echo 'no codes smells yet'
fi