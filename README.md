demo-flask
==========

Setup
-----

### Prerequisites/Assumptions

* Install mysql server on port 3306
    * This demo application will use the mysql `root` user without a password
* Install `virtualenv`
* Install `make`

### Initialization

* Create the virtualenv: `make env`
* Initialize the database: `make initdb`

Running
-------

### Running the Server

* In one terminal: `make run`
* In another terminal, execute the various endpoints
    * e.g.: `curl "http://localhost:5555/1/activity/200/available_days?from=2013-10-14&to=2013-10-16"`

### Running the Tests
```
make test
```

API
---

* GET   `/1/vendor`
* POST  `/1/vendor/create`
* GET   `/1/vendor/<vendor_id>`
* GET   `/1/vendor/<vendor_id>/activities`
* POST  `/1/vendor/<vendor_id>/create_activity`
* POST  `/1/vendor/<vendor_id>/delete_activity`

* GET   `/1/activity/<activity_id>/available_days`
* GET   `/1/activity/<activity_id>/available_times`
* GET   `/1/activity/<activity_id>/available_slots`
* POST  `/1/activity/<activity_id>/book`
* POST  `/1/activity/<activity_id>/create_slot`
* POST  `/1/activity/<activity_id>/delete_slot`
* POST  `/1/activity/<activity_id>/delete_booking`

* POST  `/1/activity/<activity_id>/generate_recurring_slots`

Data Model
----------

See the `conf/schema.sql` file.
