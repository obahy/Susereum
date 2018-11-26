#!/bin/bash
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD
add-apt-repository 'deb http://repo.sawtooth.me/ubuntu/1.0/stable xenial universe'
apt-get update



apt-get -y install cron
apt-get -y install python python2 python3
apt-get -y install sawtooth
apt-get -y install virt-what
apt-get -y install libgtk-3-dev
apt-get -y install glade
apt-get -y install devhelp
apt-get -y install gtk3
apt-get -y install curl
apt-get -y install python-tk
apt-get -y install libgirepository1.0-dev

apt-get -y install python-pip python-dev build-essential 
apt-get -y install pip 
apt-get -y install python3-pip
apt-get -y install libgirepository1.0-dev

pip install --upgrade pip
pip install --upgrade virtualenv
pip install toml
pip install pygobject
pip install pandas
pip install requests
pip install matplotlib
pip install numpy


pip3 install --upgrade pip
pip3 install --upgrade virtualenv
pip3 install toml
pip3 install pygobject
pip3 install pandas
pip3 install requests
pip3 install matplotlib
pip3 install numpy

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
