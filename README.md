# Dronut App
Drount App to manage donuts and deliver by drone

### Setting up the project
git clone from git repo in the folder of your choice

`git clone -b mster https://github.com/ifranaiyubali/dronut.git`

 #### Set up Virtual environment
 Setup virtual environment in the app folder
 `python -m venv venv`
 

 #### Activate Virtual environment

Linux 
 `source venv\Scripts\activate`
 
Windows 
 `venv\Scripts\activate.bat`

install all requirements

 `pip install -r requirements.txt`
 
 Migrate so the tables are created in database
 
 `python manage.py migrate`
 
 Run the server for testing
 `python manage.py runserver`
 

 
 #### Run tests
Test has been setup, to make sure the application functions as required. To make sure future changes do not create bugs and 
issue with current functionality 

To all test run the command `python manage.py test tests\unit_tests`

 #### Run PyLint
 To make all codes are up to standard run the following commands for code checking
 
 `pylint --load-plugins pylint_django --django-settings-module=dronut.settings dronut dronut_app tests`