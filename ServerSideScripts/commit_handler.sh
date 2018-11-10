#!/bin/bash
SENDERID=$1
REPOID=$2
COMMIT_URL=$3

#COMMIT_URL check if url has spaces?

#get chain ports
cd $(dirname "$0")/map
readarray ports < $REPOID


export SAWTOOTH_HOME="$HOME/.sawtooth_projects/.$(echo $NAME)_$(echo $ID)"
cd $SAWTOOTH_HOME

#push to chain the commit
pytho3 bin/health.py commit --url ${ports[2]} --githurl $COMMIT_URL --gituser $1 &

touch /commitran


