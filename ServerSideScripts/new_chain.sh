#!/bin/bash
NAME=$1
ID=$2
if [ -z "$NAME" ] 
then
echo "Please enter name of project: new_chain.sh [prj_name] [prj_id]"
exit 1
fi
if [ -z "$ID" ] 
then
echo "Please enter ID of project: new_chain.sh [prj_name] [prj_id]"
exit 1
fi
#echo $NAME $ID
export SAWTOOTH_HOME="$HOME/.$(echo $NAME)_$(echo $ID)"

#TODO make thread safe (else ports may conflict)
#generate ports based on availablity
STARTINGPORT=1000
ENDINGPORT=655354

for i in $(seq $STARTINGPORT $ENDINGPORT);do
port=$(lsof -i :$i)
if [ -z "$port" ]
then
#assign first port
if [ -z "$VALIDATOR_PORT_COM" ] 
then
VALIDATOR_PORT_COM=$port
fi
#assign second port
if [ -z "$VALIDATOR_PORT_NET" ] 
then
VALIDATOR_PORT_NET=$port
fi
#assign third port
if [ -z "$API_PORT" ] 
then
API_PORT=$port
break
fi
fi
done 

#check if i got all the ports
if [ -z VALIDATOR_PORT_COM ] || [ -z VALIDATOR_PORT_NET ] || [ -z API_PORT ]; then
echo 'ERROR: the system could not get an available port'
exit 1
fi

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
sawset genesis -k keys/validator.priv -o config-genesis.batch
sawset proposal create -k keys/validator.priv \
-o config.batch \
sawtooth.consensus.algorithm=poet \
sawtooth.poet.report_public_key_pem="$(cat /etc/sawtooth/simulator_rk_pub.pem)" \
sawtooth.poet.valid_enclave_measurements=$(poet enclave measurement) \
sawtooth.poet.valid_enclave_basenames=$(poet enclave basename)
poet registration create -k keys/validator.priv -o poet.batch
sawset proposal create -k keys/validator.priv \
-o poet-settings.batch \
sawtooth.poet.target_wait_time=5 \
sawtooth.poet.initial_wait_time=25 \
sawtooth.publisher.max_batches_per_block=100
sawadm genesis config-genesis.batch config.batch poet.batch poet-settings.batch

#TODO generate webpage for connection
web=$(mktemp -p /opt/lampp/htdocs/connect/)
echo $VALIDATOR_PORT_COM > $web
echo $VALIDATOR_PORT_NET >> $web
echo $API_PORT >> $web
web=$(basename -- "$web")
name=$(echo "$web" | cut -d'.' -f1)
ext=$(echo "$web" | cut -d'.' -f2)
echo "http://$IP/connect/$name.$ext"

#validator
sawtooth-validator --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$IP:$VALIDATOR_PORT_NET &
#rest api
sawtooth-rest-api -v --bind localhost:$API_PORT --connect localhost:$VALIDATOR_PORT_COM &
#processors
settings-tp -v --connect tcp://$IP:$VALIDATOR_PORT_COM &
intkey-tp-python -v --connect tcp://$IP:$VALIDATOR_PORT_COM &
#read block
sawtooth block list --url http://$IP:$API_PORT


