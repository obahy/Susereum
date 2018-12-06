#!/bin/bash
#call me from cron every min or so
#check each chain for any proposals
#TODO verify i am running!!!!
touch /home/practicum2018/p_l_ran.txt
for D in /home/practicum2018/.sawtooth_projects/.*/; #TODO make req to have one folder in home
do
	if [ "$D" == "/home/practicum2018/.sawtooth_projects/./" ] ;then
		continue
	fi
	if [ "$D" == "/home/practicum2018/.sawtooth_projects/../" ] ;then
		continue
	fi
	echo "checking: $D $(date)" >> /proposal_ran
	#start services
	readarray ports < $D/etc/.ports
	#RESULTS=$(cat $D/etc/.ports)
	cat $D/etc/.ports
	VALIDATOR_PORT_COM=$(echo ${ports[0]} | tr -d '\n')
	VALIDATOR_PORT_NET=$(echo ${ports[1]} | tr -d '\n')
	API_PORT=$(echo ${ports[2]} | tr -d '\n')
	echo "$D $VALIDATOR_PORT_COM $VALIDATOR_PORT_NET $API_PORT"
	#query to see if there is a proposal
	echo "python3 $D/bin/code_smell.py list --type proposal --active 1 --url http://127.0.0.1:$API_PORT"
	proposal=`python3 $D/bin/code_smell.py list --type proposal --active 1 --url http://127.0.0.1:$API_PORT`
	if grep -q "$proposal" <<< "Error" ;
	then
		echo "nada"
		continue #there is no proposal right now
	else
		echo "making tasks... $API_PORT"
		#check if task exists
		cron_cmd="@hourly python3 /home/practicum2018/Suserium/Susereum/ServerSideScripts/vote_listener.py $proposal $D"
		crontab -l > mycron
		echo "adding.. cron command: $cron_cmd"
		if grep -Fxq "$cron_cmd" mycron
		then
			echo -n ""
		else
			#add task
			echo "$cron_cmd" >> mycron
			crontab mycron
			
		fi
		rm mycron
	fi
done
