#!/bin/bash
NAME=$1
ID=$2
SUSEFILE=$3
echo "----------------------------------"
echo "Dummy Create New Blockchain says:"
echo "Project ID: $ID, Project Name: $NAME, Suse file Contents: $SUSEFILE"
URL='http://127.0.0.1/connect/tmp.adcewqrfd'
echo $URL
echo "----------------------------------"

# Send URL to Github script
curl --silent --request POST --url http://129.108.7.2:3000/  --header '"CONTENT_TYPE": "application/json"'  --data '{"sender": "Sawtooth", "url": "'$URL'", "repoID": "'$ID'"}'
