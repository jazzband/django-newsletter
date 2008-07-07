#!/bin/bash
PYTHON=/usr/local/bin/python
MYDIR=`dirname $BASH_SOURCE`
source /usr/local/bin/use-django
use-django r7367

if [[ $1 != "" ]]; then
	$PYTHON $MYDIR/manage.py $1
else
	screen $PYTHON $MYDIR/manage.py runserver devel.visualspace.nl:9457
fi

