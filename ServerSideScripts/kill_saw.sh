#!/bin/bash
ps -lah | grep python | grep -v git |awk '{print $3}' | xargs kill -9
