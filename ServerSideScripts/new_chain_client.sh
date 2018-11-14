#!/bin/bash
URL=$1
REPO_PATH=$2
if [ -z "$URL" ] 
then
echo "Please connecting url of project: new_chain_client.sh [url]"
exit 1
fi
RESULT=$(curl $URL)
VALIDATOR_PORT_COM=$(echo $RESULT | cut -d$' ' -f1)
VALIDATOR_PORT_NET=$(echo $RESULT | cut -d$' ' -f2)
API_PORT=$(echo $RESULT | cut -d$' ' -f3)
NAME=$(echo $RESULT | cut -d$' ' -f4)
ID=$(echo $RESULT | cut -d$' ' -f5)
SUSE=$(echo $RESULT | cut -d$' ' -f6-)
echo $SUSE

#get ip address
IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)

mkdir $HOME/.sawtooth_projects
export SAWTOOTH_HOME="$HOME/.sawtooth_projects/.$(echo $NAME)_$(echo $ID)"

mkdir $SAWTOOTH_HOME
cd $SAWTOOTH_HOME
mkdir data
mkdir logs
mkdir keys
mkdir results
chmod +w results

#make keys
sawadm keygen
sawtooth keygen

#TODO cp sawtooth families and stuff into hidden folder
cp -r $REPO_PATH/Sawtooth/* . #TODO make dynamic
wget $URL
cat "${URL##*/}" | tail -n +6 > etc/.suse
rm "${URL##*/}"


#write ports to .ports
echo $VALIDATOR_PORT_COM > etc/.ports  #TODO make ports dynamic based on host's usage
echo $VALIDATOR_PORT_NET >> etc/.ports
echo $API_PORT >> etc/.ports

#repo path
echo $REPO_PATH > etc/.repo

#ports check if in VM - set endpoint
if [[ $(virt-what) ]]; then
ENDPOINT=$(tracepath 129.108.7.2 | grep "2:" | awk '{print $2}')
else
ENDPOINT=$IP
fi


#start services
#validator
sawtooth-validator --bind component:tcp://127.0.0.1:$VALIDATOR_PORT_COM --bind network:tcp://$IP:$VALIDATOR_PORT_NET --endpoint tcp://$ENDPOINT:$VALIDATOR_PORT_NET --peers tcp://129.108.7.2:$VALIDATOR_PORT_NET & #--peers tcp://129.108.7.1:$VALIDATOR_PORT_NET &
#rest api
sawtooth-rest-api -v --bind localhost:$API_PORT --connect localhost:$VALIDATOR_PORT_COM &
#processors
settings-tp -v --connect tcp://localhost:$VALIDATOR_PORT_COM &
poet-validator-registry-tp --connect tcp://127.0.0.1:$VALIDATOR_PORT_COM &
#cd $SAWTOOTH_HOME/bin
python3 bin/codesmell-tp --connect tcp://localhost:$VALIDATOR_PORT_COM &
python3 bin/health-tp --connect tcp://localhost:$VALIDATOR_PORT_COM &




