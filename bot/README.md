Prerequirements:

- venv

Python 3.12.0, aiogram

```bash
pip install -r requirements.txt
```


# Bootstrap


Standalone:
- env

add `BOT_TOKEN` to your enviroment variables

for example:
(Linux)
```bash
export BOT_TOKEN=your_token
```
(Windows)
```shell
set BOT_TOKEN=yourtoken
```

Running:

`python main.py`



Via docker:


Building

```bash
docker build --tag 'lazy-lecture-bot' .
```

Running
```
docker run -e BOT_TOKEN=<yourtoken> -it lazy-lecture-bot
```
