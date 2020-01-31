.PHONY: clean system-packages python-packages activate-venv install tests run all database-all database-upgrade database-init docker

clean:
	sudo find . -type f -name '*.pyc' -delete
	sudo find . -type f -name '*.log' -delete
	sudo rm -rf app/main/service/image_builder/run/

system-packages:
	sudo apt update
	sudo apt install python3-venv python3-wheel python-wheel-common -y
	python3 -m venv .venv
	# sudo apt install nginx -y
	# sudo ufw allow 'Nginx Full'

python-packages: activate-venv
	pip install --upgrade pip
	pip install -r requirements.txt

activate-venv:
	. .venv/bin/activate

install: system-packages python-packages database-all

tests: activate-venv
	python manage.py test
 
run: activate-venv
	python manage.py run

database-init: activate-venv
	python manage.py db init

database-upgrade: activate-venv
	python manage.py db migrate
	python manage.py db upgrade

database-all: database-init database-upgrade

all: clean install database-all tests run

docker: database-all tests run
