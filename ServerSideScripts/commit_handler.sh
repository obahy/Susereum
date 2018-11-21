#!/bin/bash
SENDERID=$1
REPOID=$2
NAME=$3
COMMIT_URL=$4
TIME=$5
echo 'about to run'
#COMMIT_URL check if url has spaces?



#get chain ports
cd /home/practicum2018/Suserium/Susereum/ServerSideScripts/map/  #$(dirname "$0")/map #TODO make dynamic
readarray ports < $REPOID
export SAWTOOTH_HOME="$HOME/.sawtooth_projects/.$(echo $NAME)_$(echo $REPOID)"
cd $SAWTOOTH_HOME
#push to chain the commit
api=$(echo ${ports[2]} | tr -d '\n')
#get random client public key 
#transaction_id=`sawtooth transaction list --url http://127.0.0.1:$api` #TODO

python3 bin/health.py commit --url http://127.0.0.1:$api --giturl $COMMIT_URL --gituser $SENDERID --date $TIME & #--client_key &
#url is for chain api
echo "python3 $SAWTOOTH_HOME/bin/health.py commit --url http://127.0.0.1:$api --giturl $COMMIT_URL --gituser $SENDERID --date $TIME" > /commitran
echo " $SENDERID $REPOID $NAME $COMMIT_URL $TIME" >> /commitran



