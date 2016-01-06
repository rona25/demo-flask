PYTHON_ENV?=venv
MYSQL_HOST?=127.0.0.1
MYSQL_PORT?=3306
MYSQL_USER?=root
MYSQL_PWD?=
MYSQL_DB?=demo

env: virtualenv

clean:
	find . -name "*.pyc" | xargs rm -f

initdb:
	(echo "drop database $(MYSQL_DB)" | mysql -u$(MYSQL_USER) -p$(MYSQL_PWD) -h$(MYSQL_HOST) -P$(MYSQL_PORT) 2>/dev/null) || echo
	echo "create database $(MYSQL_DB)" | mysql -u$(MYSQL_USER) -p$(MYSQL_PWD) -h$(MYSQL_HOST) -P$(MYSQL_PORT)
	mysql -u$(MYSQL_USER) -p$(MYSQL_PWD) -h$(MYSQL_HOST) -P$(MYSQL_PORT) $(MYSQL_DB) < conf/schema.sql
	mysql -u$(MYSQL_USER) -p$(MYSQL_PWD) -h$(MYSQL_HOST) -P$(MYSQL_PORT) $(MYSQL_DB) < conf/testdata.sql

run:
	. venv/bin/activate ; \
		MYSQL_HOST=$(MYSQL_HOST) \
		MYSQL_PORT=$(MYSQL_PORT) \
		MYSQL_USER=$(MYSQL_USER) \
		MYSQL_PWD=$(MYSQL_PWD) \
		MYSQL_DB=$(MYSQL_DB) \
		python main.py

uwsgi:
	. venv/bin/activate ; \
		MYSQL_HOST=$(MYSQL_HOST) \
		MYSQL_PORT=$(MYSQL_PORT) \
		MYSQL_USER=$(MYSQL_USER) \
		MYSQL_PWD=$(MYSQL_PWD) \
		MYSQL_DB=$(MYSQL_DB) \
		uwsgi --ini uwsgi.conf

test:
	. venv/bin/activate ; nosetests -s test_activity.py test_booking.py test_recurring.py test_vendor.py

virtualenv:
	rm -rf $(PYTHON_ENV)
	virtualenv --no-site-packages --prompt='(demo-flask) ' $(PYTHON_ENV)
	$(PYTHON_ENV)/bin/pip install -r requirements.txt
