# Python3WebServer
A simple Python3 webserver with MySQL API support

## Features:
- Simple Frontend (view).
- Multitreaded python3 backend for serving HTTP(S) requests (src/py3server/httpRequestHandler.py)
- Makefile for easy deployment (src).
- Routes file to only serve the files you want to serve (config).
- Possible to serve over HTTPS. Simply serve on port 443 and supply the SSL cert and public key in the config directory.
- MySQL database API to store / retrieve data (src/py3server/mySQLDatabase.py).
- User and Event tables in the MySQL database.
- Interactive console.
- Custom messages for error codes 401, 404 and 418 (you can add more).
- Password hashing for users (src/py3server/passwordHashing.py).
- Possible to create users, login via the frontend, and stay logged in for a set amount of time via cookies.
- Stand-alone webscraper to scrape and parse events into a file (src/py3server/webScraper.py).
- WIP code for creating .ics event files that can be build off of (src/py3server/calenderEvent.py).

## Tested/Supported platform(s)
- Ubuntu 20.04.6 LTS Linux
- Python version: 3.8.10
- Make version: GNU Make 4.2.1

(You can probably get it working on Windows with relative ease by changing the Makefile, or by invoking src/py3Backend.py manually from the terminal)

<img width="960" alt="py3webserverindex" src="https://github.com/user-attachments/assets/348ce0e3-6434-4b47-83e4-423d43a55e36">

<img width="813" alt="py3webserverConsole" src="https://github.com/user-attachments/assets/8d5e2024-762a-470d-b8b1-ca4d65de0703">

