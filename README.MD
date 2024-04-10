## Django Chat tutorial which I will expand with more functionality for 42 Transcendence Project.
http://127.0.0.1:8000/chat/

start the server:
dependency redis:
docker run --rm -p 6379:6379 redis:7
--rm to remove the container after it stops running.

python3 manage.py runserver

### Useful commands
python3 -m django --version

django-admin startproject mychat
python -m pip install -U 'channels[daphne]'
python3 -m pip install channels_redis

python manage.py migrate