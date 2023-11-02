#! /bin/sh
echo '' > ./crontab
echo "${CRON_LINE} python main.py > /dev/stdout" >> ./crontab
/usr/local/bin/supercronic ./crontab
/usr/local/bin/supercronic -l