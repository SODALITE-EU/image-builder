.PHONY: clean system-packages python-packages install tests run all database database-upgrade database-init docker

clean:
	sudo find . -type f -name '*.pyc' -delete
	sudo find . -type f -name '*.log' -delete
	sudo rm -rf app/main/service/image_builder/run/

system-packages:
	sudo apt update
	sudo apt install python3-pip -y

python-packages:
	pip3 install --upgrade pip
	pip3 install -r requirements.txt

install: system-packages python-packages database

tests:
	python3 manage.py test
 
run:
	python3 manage.py run

database-init:
	python3 manage.py db init

database-upgrade:
	python3 manage.py db migrate
	python3 manage.py db upgrade

database: database-init database-upgrade

all: clean install database tests run
