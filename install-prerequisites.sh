#!/bin/bash

# pro gtk na desktopu sudo apt-get install python-gtk2 

### install deb packages ###
sudo apt-get install -y python-dev swig libboost-python-dev python-pip make gcc g++ socat  git build-essential libudev-dev libusb-dev cmake autoconf libtool pkg-config rbp2-libcec-dev-osmc rbp2-libcec-osmc rbp-userland-dev-osmc rbp-userland-dev-osmc liblockdev1-dev libxrandr-dev python-dev

### install pip ###
sudo pip install astral web.py python-uinput

### shnopp kodi service ###
rm -f ~/.kodi/addons/service.shnopp-kodi
ln -s ~/shnopp/service.shnopp-kodi ~/.kodi/addons/service.shnopp-kodi
ln -s ~/shnopp/config ~/.kodi/addons/service.shnopp-kodi/config
ln -s ~/shnopp/misc ~/.kodi/addons/service.shnopp-kodi/misc
        
### BT audio kodi service ###
rm -f ~/.kodi/addons/service.sc-np10
ln -s ~/shnopp/service.sc-np10 ~/.kodi/addons/service.sc-np10


### init.d ###
sudo rm -f /etc/init.d/shnopp
sudo ln -s /home/osmc/shnopp/shnoppinit /etc/init.d/shnopp

sudo chmod 755 /etc/init.d/shnopp
sudo chown root:root /etc/init.d/shnopp

sudo update-rc.d shnopp defaults
sudo update-rc.d shnopp enable

### restart kodi ###
sudo setsid /usr/sbin/service mediacenter --full-restart

### install A2DP ###
wget http://paste.osmc.io/raw/qiyekuvafe -O- | sudo sh
