#!/bin/bash
d=`date +%m-%d-%Y`
mv archivos/logs/errors.txt archivos/logs/$d-errors.txt
touch archivos/logs/errors.txt
mv archivos/logs/apis.txt archivos/logs/$d-apis.txt
touch archivos/logs/apis.txt
mv archivos/logs/tasks.txt archivos/logs/$d-tasks.txt
touch archivos/logs/tasks.txt
mv archivos/logs/signals.txt archivos/logs/$d-signals.txt
touch archivos/logs/signals.txt

