#!/bin/bash
echo "practicum2018" | sudo -S su
crontab -l > $1
