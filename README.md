# scraping_amolatina
Scraping to Web Site


su - root
apt-get install supervisor
systemctl start supervisor.service
systemctl enable supervisor.service

cat << EOF > /etc/supervisor/conf.d/amolatina.conf
[program:amolatina]
command=su -c "/usr/bin/python3 /home/admin01/scraping/amolatina.py" admin01
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 60
stderr_logfile=/var/log/supervisor/amolatina.err.log
stdout_logfile=/var/log/supervisor/amolatina.out.log
killasgroup=true
priority=998
EOF

supervisorctl reread
supervisorctl update

supervisorctl status
supervisorctl restart all
supervisorctl stop all
supervisorctl start all