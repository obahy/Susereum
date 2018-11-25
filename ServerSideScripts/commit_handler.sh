#!/bin/bash
SENDERID=$1
REPOID=$2
NAME=$3
COMMIT_URL=$4
TIME=$5
echo 'about to run'
#COMMIT_URL check if url has spaces?



#get chain ports
Dir=$(
cd $(dirname "$0")
pwd
)
readarray ports < $Dir/map/$REPOID
export SAWTOOTH_HOME="$HOME/.sawtooth_projects/.$(echo $NAME)_$(echo $REPOID)"
cd $SAWTOOTH_HOME
#push to chain the commit
api=$(echo ${ports[2]} | tr -d '\n')
#get random client public key 
transaction_id=`sawtooth transaction list --url http://127.0.0.1:1002 | tail -n +2 | shuf -n 1 | awk '{print $1;}'`
key=`sawtooth transaction show $transaction_id  --url http://127.0.0.1:$api | grep signer_public_key | awk '{print $2;}'`
python3 bin/health.py commit --url http://127.0.0.1:$api --giturl $COMMIT_URL --gituser $SENDERID --date $TIME --client_key $key &
#url is for chain api
echo "python3 $SAWTOOTH_HOME/bin/health.py commit --url http://127.0.0.1:$api --giturl $COMMIT_URL --gituser $SENDERID --date $TIME" > /commitran
echo " $SENDERID $REPOID $NAME $COMMIT_URL $TIME" >> /commitran



