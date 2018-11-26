#!/bin/bash
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD
add-apt-repository 'deb http://repo.sawtooth.me/ubuntu/1.0/stable xenial universe'
apt-get update



apt-get -y install cron
apt-get -y install python python2 python3
apt-get -y install sawtooth
apt-get -y install virt-what
apt-get -y install gtk3
apt-get -y install glade
apt-get -y install devhelp
apt-get -y install gtk3
apt-get -y install toml
apt-get -y install curl
apt-get -y install python-tk

apt-get install python-pip python-dev build-essential 
pip install --upgrade pip
pip install --upgrade virtualenv

pip install pygobject
pip install pandas
pip install requests
pip install matplotlib
pip install pygobject 

#start services on reboot - cron task
Dir=$(
cd $(dirname "$0")
pwd
)
crontab -l > mycron
echo "@reboot $Dir/startup.sh" >> mycron
#echo "3 * * * * $Dir/proposal_listener.sh" #this is only for server
crontab mycron
rm mycron


mkdir ~/.sawtooth_projects

echo 'you can know use Suserium :D'
echo 'make sure to copy Source Meter into folder'



#open source meter webpage
