#!/bin/bash
wrapper=$1
url=$2
results=$3
src_dir=$4
cd $src_dir
touch imruning
echo "echo practicum2018 | sudo -S python2.7 $repo_path $github_url $sawtooth_home"
echo "practicum2018" | sudo -S python2.7 $wrapper $url $results
touch iran
