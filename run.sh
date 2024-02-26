#!/usr/bin/with-contenv bashio

#echo "Hello world!"

bashio::log.blue " Starting Onzo energy monitor..."
bashio::log  "Output from lsusb..."

#env
#lsusb -h

python3 -V
python read.py
