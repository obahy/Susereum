#!/bin/bash
URL=$1
if [ -z "$URL" ] 
then
echo "Please enter name of project: new_chain_client.sh [url]"
exit 1
fi
curl $URL

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

#TODO cp sawtooth families and stuff into hidden folder

#start services
#validator
sudo sawtooth-validator --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$IP:$VALIDATOR_PORT_NET &
#rest api
sawtooth-rest-api -v --bind localhost:$API_PORT --connect localhost:$VALIDATOR_PORT_COM &
#processors
sudo settings-tp -v --connect tcp://$IP:$VALIDATOR_PORT_COM &
cd $SAWTOOTH_HOME/bin
sudo code_smell-tp -v --connect tcp://$IP:$VALIDATOR_PORT_COM &


