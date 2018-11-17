#!/bin/bash
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD
add-apt-repository 'deb http://repo.sawtooth.me/ubuntu/1.0/stable xenial universe'
apt-get update



apt-get -y install cron
apt-get -y install python
apt-get -y install sawtooth
apt-get -y install virt-what
apt-get -y install gtk3
apt-get -y install glade
apt-get -y install devhelp
apt-get -y install python3
apt-get -y install python2
apt-get -y install toml
apt-get -y install curl
apt-get -y install python-tk

pip install pygobject
pip install pandas
pip install requests
pip install matplotlib

#start services on reboot


mkdir ~/.sawtooth_projects

echo 'you can know use Suserium :D'
echo 'make sure to copy Source Meter into folder'



#open source meter webpage
