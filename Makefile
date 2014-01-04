PYTHON_ENV?=venv
MYSQL_USER?=root

env: virtualenv

clean:
	find . -name "*.pyc" | xargs rm -f

initdb:
	(echo "drop database demo" | mysql -u$(MYSQL_USER) 2>/dev/null) || echo
	mysql -u$(MYSQL_USER) < conf/schema.sql
	mysql -u$(MYSQL_USER) < conf/testdata.sql

run:
	. venv/bin/activate ; python main.py

test:
	. venv/bin/activate ; nosetests -s test_activity.py test_booking.py test_recurring.py test_vendor.py

virtualenv:
	rm -rf $(PYTHON_ENV)
	virtualenv --no-site-packages --prompt='(demo-flask) ' $(PYTHON_ENV)
	$(PYTHON_ENV)/bin/pip install -r requirements.txt
