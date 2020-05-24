import os
import multiprocessing


loglevel = 'info'
errorlog = '/var/log/gunicorn-error.log'
accesslog = '/var/log/gunicorn-access.log'

bind = '0.0.0.0:5000'
workers = multiprocessing.cpu_count() * 2 + 1

timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

capture_output = True
