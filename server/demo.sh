#!/bin/sh

printf 'Creating/Activating virtual python environment...\n'
python3 -m venv venv
source venv/bin/activate
echo '--DONE--'

printf  '\nInstalling project libraries...\n'
pip install --upgrade pip && pip install -r requirements.txt
echo '--DONE--'

printf  '\nExecuting tests...\n'
python manage.py test apps
echo '--DONE--'

printf  '\nSetting up development database...\n'
python manage.py migrate
echo '--DONE--'

printf  '\nLoading demo fixtures...\n'
python manage.py loaddata happiness_demo
echo '--DONE--'

printf  '\n\n'
python manage.py runserver
