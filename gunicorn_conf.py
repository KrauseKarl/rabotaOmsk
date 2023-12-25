from multiprocessing import cpu_count

bind = "127.0.0.1:8002"

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/home/alice/rabotaOmsk/rabotaOmsk/logs/gunicorn/access_log'
errorslog = '/home/alice/rabotaOmsk/rabotaOmsk/logs/gunicorn/error_log'
