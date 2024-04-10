## Django Chat tutorial
I will expand this tutorial with more functionality for 42 Transcendence Project.

http://127.0.0.1:8000/chat/

- dependency redis
docker run --rm -p 6379:6379 redis:7

--rm to remove the container after it stops running.

- start the server:
python3 manage.py runserver

### Useful commands
python3 -m django --version

django-admin startproject mychat

python -m pip install -U 'channels[daphne]'

python3 -m pip install channels_redis

python manage.py migrate
