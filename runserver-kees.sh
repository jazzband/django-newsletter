#!/usr/local/bin/bash
source /usr/local/bin/use-django
use-django r7367
if [[ $1 == "shell" ]]; then
	python manage.py shell
else
	screen python manage.py runserver devel.visualspace.nl:9458
fi

