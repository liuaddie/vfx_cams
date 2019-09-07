# chmod 777 env_setup.command
sudo virtualenv -p python "$(dirname "$0")/../env/"
sudo pip install --upgrade pip
sudo pip install -r "$(dirname "$0")/../requirements.txt"
