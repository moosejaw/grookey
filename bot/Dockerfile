FROM python:3.7-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY bot.py ./
COPY emojis ./

CMD ["python3", "bot.py"]