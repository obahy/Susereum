#!/bin/bash
#check each chain for any proposals
for D in `find . -type d`
do
#start services
RESULTS=$(cat $D/etc/.ports)
VALIDATOR_PORT_COM=$(echo $RESULT | cut -d$' ' -f1)
VALIDATOR_PORT_NET=$(echo $RESULT | cut -d$' ' -f2)
API_PORT=$(echo $RESULT | cut -d$' ' -f3)



done
