FROM python:3.12

WORKDIR /bot

COPY main.py /bot
COPY requirements.txt /bot

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["python", "-u", "main.py"]