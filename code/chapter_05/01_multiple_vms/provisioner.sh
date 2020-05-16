#!/bin/bash

apt-get update
apt-get install -y nginx
sudo cp /vagrant/index.html /var/www/html