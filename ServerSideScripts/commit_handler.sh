#!/bin/bash
SENDERID=$1
REPOID=$2
COMMIT_URL=$3

#get chain ports
cd map
readarray ports < $REPOID


export SAWTOOTH_HOME="$HOME/.sawtooth_projects/.$(echo $NAME)_$(echo $ID)"
cd $SAWTOOTH_HOME

#push to chain the commit
pytho3 bin/health.py commit --url ${ports[2]} --githurl $COMMIT_URL --gituser $1


