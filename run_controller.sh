#!/bin/bash

cd /root/repo/vfx_cams/
git pull origin master
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 controller.py
