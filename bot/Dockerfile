FROM python:3.12

WORKDIR /bot

COPY requirements.txt /bot
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt
COPY . /bot

CMD ["python", "-u", "main.py"]
