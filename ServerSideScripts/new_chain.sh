#!/bin/bash
#sudo su
NAME=$1
ID=$2
SUSE_PATH=$3
REPO_PATH="/home/practicum2018/Suserium/Susereum/"
touch /new_chain_ran.txt
if [ -z "$NAME" ] 
then
echo "Please enter name of project: new_chain.sh [prj_name] [prj_id] [suse_file]"
exit 1
fi
if [ -z "$ID" ] 
then
echo "Please enter ID of project: new_chain.sh [prj_name] [prj_id] [suse_file]"
exit 1
fi
echo $NAME $ID
export SAWTOOTH_HOME="$HOME/.sawtooth_projects/.$(echo $NAME)_$(echo $ID)"

#TODO make thread safe (else ports may conflict)
#generate ports based on availablity
STARTINGPORT=1000
ENDINGPORT=655354

for i in $(seq $STARTINGPORT $ENDINGPORT);do
port=$(netstat -an | grep "LISTEN" | grep "$i ")
echo trying port - $port - $i
if [ -z "$port" ]
then
#assign first port
if [ -z "$VALIDATOR_PORT_COM" ] 
then
VALIDATOR_PORT_COM=$i
echo I set $VALIDATOR_PORT_COM
continue
fi
#assign second port
if [ -z "$VALIDATOR_PORT_NET" ] 
then
VALIDATOR_PORT_NET=$i
echo I set $VALIDATOR_PORT_NET
continue
fi
#assign third port
if [ -z "$API_PORT" ] 
then
API_PORT=$i
echo I set $API_PORT
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


#map repo id to ports
mkdir $(dirname "$0")/map
cd $(dirname "$0")/map
echo $VALIDATOR_PORT_COM > $ID
echo $VALIDATOR_PORT_NET >> $ID
echo $API_PORT >> $ID

#create chain
mkdir $SAWTOOTH_HOME
cd $SAWTOOTH_HOME
mkdir data
mkdir logs
mkdir keys
mkdir results
chmod 777 results
cp -r ~/Suserium/Susereum/Sawtooth/* .
cp $SUSE_PATH etc/.suse


#write ports to .ports
echo $VALIDATOR_PORT_COM > etc/.ports  #TODO make ports dynamic based on host's usage
echo $VALIDATOR_PORT_NET >> etc/.ports
echo $API_PORT >> etc/.ports

#repo path
echo $REPO_PATH > etc/.repo


#make keys
sawadm keygen
sawtooth keygen

sawset genesis -k keys/validator.priv -o config-genesis.batch

sawset proposal create -k keys/validator.priv -o config.batch \
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
#sleep 3
#TODO generate webpage for connection
web=$( mktemp -p /opt/lampp/htdocs/connect/)
echo $VALIDATOR_PORT_COM > $web
echo $VALIDATOR_PORT_NET >> $web
echo $API_PORT >> $web
echo $NAME >> $web
echo $ID >> $web
cat $SUSE_PATH >> "$web"
chmod +r $web
web=$(basename -- "$web")
name=$(echo "$web" | cut -d'.' -f1)
ext=$(echo "$web" | cut -d'.' -f2)
#TODO send url via netcat to port 3000
URL="http://$IP/connect/$name.$ext"
echo "http://$IP/connect/$name.$ext"
curl --silent --request POST --url http://129.108.7.2:3000/  --header '"CONTENT_TYPE": "application/json"'  --data '{"sender": "ConfigurationURL", "url": "'$URL'", "repoID": "'$ID'"}'
cat /opt/lampp/htdocs/connect/$web #TODO delete me on the first proposal
#rm $SUSE_PATH

#start services
#validator
sawtooth-validator -vv --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$IP:$VALIDATOR_PORT_NET --peering dynamic &
#sleep 3
#rest api
sawtooth-rest-api -v --bind localhost:$API_PORT --connect 127.0.0.1:$VALIDATOR_PORT_COM &
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

#TODO call default - url-validator, and sawtooth repo ($SAWTOOTH_HOME/Sawtooth)
#python3 families/code-smell/client/code_smell.py default --url http://127.0.0.1:$VALIDATOR_PORT_COM --path $SAWTOOTH_HOME 


#make this persistant - append service commands to a script that will run on reboot


