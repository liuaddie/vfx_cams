# chmod 777 env_start.command
source "$(dirname "$0")/../env/bin/activate"
sudo pip install --upgrade pip
sudo pip install -r "$(dirname "$0")/../requirements.txt"
