Prerequirements:

- venv

Python 3.12.0, aiogram

```
pip install -r requirements.txt
```


# Bootstrap


Standalone:
- env

add `BOT_TOKEN` to your enviroment variables

for example: 
```
export BOT_TOKEN=your_token
```

Running:

`python main.py`



Via docker:


Building

```
docker build --tag 'lazy-lecture-bot' .
```

Running
```
docker run -e BOT_TOKEN=<yourtoken> -it lazy-lecture-bot
```
