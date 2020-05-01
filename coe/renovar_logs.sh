#!/bin/bash
d=`date +%m-%d-%Y`
mv archivos/logs/errors.txt archivos/logs/$d-errors.txt
touch archivos/logs/errors.txt
mv archivos/logs/apis.txt archivos/logs/$d-apis.txt
touch archivos/logs/apis.txt
mv archivos/logs/apis.txt archivos/logs/$d-apis.txt
touch archivos/logs/apis.txt