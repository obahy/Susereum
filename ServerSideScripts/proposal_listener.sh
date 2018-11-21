#!/bin/bash
#check each chain for any proposals
for D in /home/practicum2018/.sawtooth_projects/.*/;
do
if [ "$D" == "/home/practicum2018/.sawtooth_projects/./" ] ;then
continue
fi
if [ "$D" == "/home/practicum2018/.sawtooth_projects/../" ] ;then
continue
fi
#start services
readarray ports < $D/etc/.ports
#RESULTS=$(cat $D/etc/.ports)
VALIDATOR_PORT_COM=$(echo ${ports[0]} | tr -d '\n')
VALIDATOR_PORT_NET=$(echo ${ports[1]} | tr -d '\n')
API_PORT=$(echo ${ports[2]} | tr -d '\n')
echo "$D $VALIDATOR_PORT_COM $VALIDATOR_PORT_NET $API_PORT"


done
