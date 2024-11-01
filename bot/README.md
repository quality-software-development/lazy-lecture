Prerequirements:

- venv

Python 3.12.0, aiogram

```
pip install -r requirements.txt
```

- env

add `BOT_TOKEN` to your enviroment variables


Building

```
docker build --tag 'lazy-lecture-bot' .
```

Running
```
docker run -e BOT_TOKEN=yourtoken -it lazy-lecture-bot
```
