#!/bin/bash
clear
PROJECT="/home/devclub/Projects/grade_view/grades"
cd $PROJECT
. venv/bin/activate  #Activate your virtual environment
python3 app.py 2> access_log.txt
