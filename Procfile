release: cd bookslikethis && python manage.py migrate && python manage.py warm_cache
web: gunicorn --pythonpath bookslikethis bookslikethis.wsgi --preload --log-level debug --log-file -
