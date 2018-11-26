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
for D in ~/.sawtooth_projects/.*/;
do
if [ "$D" == "~/.sawtooth_projects/./" ] ;then
continue
fi
if [ "$D" == "~/.sawtooth_projects/../" ] ;then
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
sawtooth-validator --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$ENDPOINT:$VALIDATOR_PORT_NET --peers tcp://129.108.7.2:$VALIDATOR_PORT_NET & #--peers tcp://129.108.7.1:$VALIDATOR_PORT_NET &
#rest api
sawtooth-rest-api -v --bind 127.0.0.1:$API_PORT --connect 127.0.0.1:$VALIDATOR_PORT_COM &
#processors
settings-tp -v --connect tcp://127.0.0.1:$VALIDATOR_PORT_COM &
poet-validator-registry-tp --connect tcp://127.0.0.1:$VALIDATOR_PORT_COM &
#cd $SAWTOOTH_HOME/bin
python3 bin/codesmell-tp --connect tcp://localhost:$VALIDATOR_PORT_COM &
python3 bin/health-tp --connect tcp://localhost:$VALIDATOR_PORT_COM &

done
