#!/bin/bash
#ports check if in VM - set endpoint
if [[ $(virt-what) ]]; then
ENDPOINT=$IP
else
ENDPOINT=$(tracepath 129.108.7.2 | grep "2:" | awk '{print $2}')
fi

#start each project
for D in `find . -type d`
do
#start services
RESULTS=$(cat $D/etc/.ports)
VALIDATOR_PORT_COM=$(echo $RESULT | cut -d$' ' -f1)
VALIDATOR_PORT_NET=$(echo $RESULT | cut -d$' ' -f2)
API_PORT=$(echo $RESULT | cut -d$' ' -f3)



#start services
#validator
sawtooth-validator --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$ENDPOINT:$VALIDATOR_PORT_NET --peers tcp://129.108.7.2:$VALIDATOR_PORT_NET & #--peers tcp://129.108.7.1:$VALIDATOR_PORT_NET &
#rest api
sawtooth-rest-api -v --bind localhost:$API_PORT --connect localhost:$VALIDATOR_PORT_COM &
#processors
settings-tp -v --connect tcp://localhost:$VALIDATOR_PORT_COM &
#cd $SAWTOOTH_HOME/bin
python3 bin/codesmell-tp --connect tcp://localhost:$VALIDATOR_PORT_COM &
python3 bin/health-tp --connect tcp://localhost:$VALIDATOR_PORT_COM &
done
