#!/bin/bash
SENDERID=$1
REPOID=$2
NAME=$3
COMMIT_URL=$4
touch /startcommit
echo 'about to run'
#COMMIT_URL check if url has spaces?

#get chain ports
cd /home/practicum2018/Suserium/Susereum/ServerSideScripts/map/  #$(dirname "$0")/map #TODO make dynamic
cd $SAWTOOTH_HOME

#push to chain the commit
python3 bin/health.py commit --url http://127.0.0.1:${ports[2]} --giturl $COMMIT_URL # --gituser $SENDERID &
#url is for chain api
touch /commitran
echo "python3 bin/health.py commit --url http://127.0.0.1:${ports[2]} --giturl $COMMIT_URL" > /commitran


