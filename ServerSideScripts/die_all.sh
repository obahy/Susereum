#!/bin/bash
ps aux | grep python | grep -v git |awk '{print $2}' | xargs kill -9
rm map/*
rm /opt/lampp/htdocs/connect/*
rm -rf /home/practicum2018/.sawtooth_projects/.*
