#!/bin/bash
URL=$1
if [ -z "$URL" ] 
then
echo "Please connecting url of project: new_chain_client.sh [url]"
exit 1
fi
RESULT=$(curl $URL)
port1=$(echo $RESULT | cut -d$' ' -f1)
port2=$(echo $RESULT | cut -d$' ' -f2)
port3=$(echo $RESULT | cut -d$' ' -f3)
SUSE=$(echo $RESULT | cut -d$' ' -f4-)

echo $SUSE

#get ip address
IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)

mkdir $SAWTOOTH_HOME
cd $SAWTOOTH_HOME
mkdir data
mkdir logs
mkdir keys

#make keys
sawadm keygen
sawtooth keygen


#TODO cp sawtooth families and stuff into hidden folder
cp -r ~/Suserium/Susereum/Sawtooth/* .
echo $SUSE >. suse

#start services
#validator
sawtooth-validator --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$IP:$VALIDATOR_PORT_NET --peers tcp://129.108.7.2:$VALIDATOR_PORT_NET &
#rest api
sawtooth-rest-api -v --bind localhost:$API_PORT --connect localhost:$VALIDATOR_PORT_COM &
#processors
settings-tp -v --connect tcp://$IP:$VALIDATOR_PORT_COM &
#cd $SAWTOOTH_HOME/bin
code_smell-tp -v --connect tcp://$IP:$VALIDATOR_PORT_COM &


