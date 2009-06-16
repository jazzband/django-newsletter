#!/usr/local/bin/bash
PYTHON=`whereis python`
MYDIR=`dirname $BASH_SOURCE`

source /usr/local/bin/use-django
use-django r7966

cd $MYDIR

PWD=`pwd`
BASEPATH=`basename $PWD`
if [[ $1 != "" ]]; then
    $PYTHON manage.py $1
else
    screen -S $BASEPATH $PYTHON manage.py runserver `hostname`:9457
fi


