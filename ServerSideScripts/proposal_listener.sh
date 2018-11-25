#!/bin/bash
#call me from cron every min or so
#check each chain for any proposals
for D in $HOME/.sawtooth_projects/.*/;
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
	proposal=`python3 $D/../Sawtooth/bin/code_smell.py list --type proposal --active 1`
	if [ -z "$proposal" ]
	then
		continue
	else
		#check if task exists
		proposal_id=$(echo -n "$proposal" | awk "{print $1;}")
		proposal_date=$(echo -n "$proposal" | awk "{print $2;}")
		cron_cmd="* */1 * * * python3 vote_listener.py $proposal_id $proposal_date $D"
		crontab -l > mycron
		if grep -Fxq "$cron_cmd" mycron
		then
			ls
		else
			#add task
			echo $cron_cmd >> mycron
			crontab mycron
		fi
		rm mycron
	fi
done
