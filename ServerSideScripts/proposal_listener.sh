#!/bin/bash
#call me from cron every min or so
#check each chain for any proposals
for D in /home/practicum2018/.sawtooth_projects/.*/;
do
if [ "$D" == "$HOME/.sawtooth_projects/./" ] ;then
continue
fi
if [ "$D" == "$HOME/.sawtooth_projects/../" ] ;then
continue
fi
echo "checking: $D"
#start services
readarray ports < $D/etc/.ports
#RESULTS=$(cat $D/etc/.ports)
VALIDATOR_PORT_COM=$(echo ${ports[0]} | tr -d '\n')
VALIDATOR_PORT_NET=$(echo ${ports[1]} | tr -d '\n')
API_PORT=$(echo ${ports[2]} | tr -d '\n')
echo "$D $VALIDATOR_PORT_COM $VALIDATOR_PORT_NET $API_PORT"
#query to see if there is a proposal

#perform periodic check

days=`cat etc/.suse | grep proposal_active_days= | cut -c 22-`
votes=`cat etc/.suse | grep approval_treshold= | cut -c 19-`

done
