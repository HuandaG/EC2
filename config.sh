#!/bin/bash
# Actualiza los paquetes
sudo dnf update -y

# Instala dependencias necesarias
sudo dnf install -y git python3 python3-virtualenv

# Ir al home del usuario
cd /home/ec2-user

# Clonar el repositorio desde GitHub
git clone https://github.com/HuandaG/EC2.git || true
cd EC2

# Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copiar el archivo del servicio al sistema
sudo cp fastapi.srv /etc/systemd/system/fastapi.srv

# Recargar servicios, habilitar y arrancar el servicio
sudo systemctl daemon-reload
sudo systemctl enable fastapi.srv
sudo systemctl start fastapi.srv
