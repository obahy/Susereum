#!/bin/bash
ps aux | grep python | grep -v git |awk '{print $2}' | xargs kill -9
