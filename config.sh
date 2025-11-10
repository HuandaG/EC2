#!/bin/bash
sudo yum update -y
sudo yum install -y git python3 python3-venv

cd /home/ec2-user
git clone https://github.com/HuandaG/EC2.git
cd taller_ec2

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo cp fastapi.srv /etc/systemd/system/fastapi.srv
sudo systemctl daemon-reload
sudo systemctl enable fastapi.srv
sudo systemctl start fastapi.srv
