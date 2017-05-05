# Mysterium Network API

API for Node & Client



## Setup [![pyVersion27](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/download/releases/2.7/) 

Install the requirements using pip
```
$ pip install -r requirements.txt
```

Running
```
$ python app.py
```
Should be running on http://127.0.0.1:5000/

## Database setup

Make sure you have MySQL installed.

Create new database.

File settings.py contains database credentials, setup it.

Create tables from models:
```
$ python manual_create_db.py
```
