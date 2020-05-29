#!/bin/bash
cd /opt/coe
source venv/bin/activate
cd /opt/coe/coe
/opt/coe/venv/bin/gunicorn coe.wsgi -t 600 -b 127.0.0.1:8010 -w 6 --user=servidor --group=servidor --log-file=/opt/coe/gunicorn.log 2>>/opt/coe/gunicorn.log

