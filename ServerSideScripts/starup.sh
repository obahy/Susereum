#!/bin/bash
#get ip address
IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)

#ports check if in VM - set endpoint
if [[ $(virt-what) ]]; then
ENDPOINT=$IP
else
ENDPOINT=$(tracepath 129.108.7.2 | grep "2:" | awk '{print $2}')
fi

#start each project
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


#start services
#validator
sawtooth-validator -vv --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$ENDPOINT:$VALIDATOR_PORT_NET --peering dynamic &
#sleep 3
#rest api
sawtooth-rest-api -v --bind 0.0.0.0:$API_PORT --connect 127.0.0.1:$VALIDATOR_PORT_COM &
#sleep 3
#processors
settings-tp -v --connect tcp://127.0.0.1:$VALIDATOR_PORT_COM &
#sleep 3
poet-validator-registry-tp --connect tcp://127.0.0.1:$VALIDATOR_PORT_COM &
#intkey-tp-python -v --connect tcp://$IP:$VALIDATOR_PORT_COM &
#read block
#sawtooth block list --url http://$IP:$API_PORT
python3 bin/codesmell-tp --connect tcp://127.0.0.1:$VALIDATOR_PORT_COM &
python3 bin/health-tp --connect tcp://127.0.0.1:$VALIDATOR_PORT_COM &

done
