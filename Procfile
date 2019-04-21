release: cd bookslikethis && python manage.py migrate && python manage.py warm_cache
web: bin/start-nginx newrelic-admin run-program gunicorn --pythonpath bookslikethis bookslikethis.wsgi -c config/gunicorn.py --preload --log-level debug --log-file -
