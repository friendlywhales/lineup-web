
LINEUP backend
================

Installation
---------------

### Mac OS

```
xcode-select install
brew install libxmlsec1
pip install -r requirements.txt
```

### Ubuntu 16

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y build-essential
sudo apt update
sudo apt upgradable --list
sudo apt upgrade
sudo apt install libmysqlclient-dev
sudo apt install libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev
sudo apt install libxml2-dev libxmlsec1-dev

sudo apt-get install python3.6
sudo apt install python3.6-venv
sudo apt install python3.6-dev
python3.6 -m venv ~/lineup_venv
```

front-end 를 서버에서 빌드하려면 node.js 를 설치해야 하나 매우 느려서 권장하지 않음.
```
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install yarn -g
yarn install
```


### run up server

- commands : `start`, `stop`, `restart`

#### 실 서버

```
sudo systemctl start lineup-was.service   # WAS
sudo systemctl start celery-prod.service  # Celery
```

#### 스테이징 서버

```
sudo systemctl start lineup-was-staging.service   # WAS
sudo systemctl start celery-staging.service  # Celery
```
