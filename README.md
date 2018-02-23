# Customer Fault Management Tool

## A tool for specific customer impact Pronto statics generation

author: Yulin Xian <br>
Date: 2018/02/23 <br>
Revision: 1.0

## Feature

- Import the PR source from PR tool
- Grep customer related PR
- Get customer impacted PR trend and statistics status
- Customer rule management
- Export to excel


## Works on

- Linux
- Windows
- Mac OS


## How to install (deployment)

### Common install

- Python (v2.7) should be installed in linux or windows.

- Python environment
  * $ sudo apt-get install python-setuptools
  * $ sudo easy_install pip
  

- Install python virtualenv

  * Install virtualenv
    * $ sudo pip install virtualenv
  * Create virtualenv
    * $ virtualenv --no-site-packages venv
  * Enter virtualenv
    * $ source venv/bin/activate
  * If you want to exit venv
    * $ deactivate
  * If you want to remove venv
    * $ rm -r venv

- Install MySQL and setup database
  * refer to https://dev.mysql.com/doc/refman/5.7/en/installing.html to install mysql
  * Create a new database name 'db_flask'

- Install git and git clone project from git
  * Install git
    * $ sudo pip install git
  * git clone
    * $ git clone https://github.com/bullton/cfmtool2.git

- Prepare project environments
  * Activate venv and enter project folder
  * Install project requrements
    * $ pip install -r requirements.txt
    * @windows need to install mysql-python manually
  * DB migrate
    * $ python manage.py db init
	* $ python manage.py db migrate
	* $ python manage.py db upgrade


  
### Run and deployment

- If you just run in develop mode:
  * $ python firstflask.py

- nginx + uwsgi deployment:
  * Install nginx:
    * $ sudo apt-get install nginx
  * Install uWSGI
    * $ sudo apt-get install build-essential python-dev
    * venv $ pip install uwsgi           (Install uwsgi under python virtualenv)
  * configure nginx
    * Remove nginx default config
      * $ sudo rm /etc/nginx/sites-enabled/default
    * Edit project nginx config 'cfmtool_nginx.conf'
        ``` conf
        server { 
          listen 8080;   # This is port when you browse this tool in webbrowser
          server_name 10.106.218.58;    # your server IP address
          location / { 
          include uwsgi_params;
          uwsgi_pass 127.0.0.1:3031;
          uwsgi_param UWSGI_PYHOME /home/ute/flask/venv;    # change to you own python virtualenv folder
          uwsgi_param UWSGI_CHDIR /home/ute/flask/cfmtool2;    # your project folder
          uwsgi_param UWSGI_SCRIPT firstflask:app; 
          uwsgi_read_timeout 100; 
         }  
        }
        ``` 
  * Config uwsgi:
    * Edit project uwsgi ini file 'cfmtool_uwsgi.ini'
        ``` ini
        [uwsgi]
        master = true
        home = /home/ute/flask/venv      # change to you own python virtualenv folder
        wsgi-file = firstflask.py
        callable = app
        socket = :3031
        processes = 4
        threads = 2
        buffer-size = 32768
        ``` 
  * Install and config supervisor
    * Install
      * $ sudo apt-get install supervisor 
    * Edit project supervisor conf file 'cfmtool_supervisor.conf'
        ``` conf
        [program:cfmtool2] 
        command=/home/ute/flask/venv/bin/uwsgi /home/ute/flask/cfmtool2/cfmtool_uwsgi.ini     # your own uwsgi path in venv and uwsgi ini path       
        directory=/home/ute/flask/cfmtool2    # your project folder
        user=ute      # change to your user name 
        autostart=true
        autorestart=true
        stdout_logfile=/home/ute/flask/cfmtool2/logs/uwsgi_supervisor.log      # define supervisor log   
        [supervisord]
        ``` 
  * Run with supervisor
    * $ supervisord -c xxx.conf 
 