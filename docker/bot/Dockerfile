FROM python:3.8-slim

WORKDIR /usr/src/app
COPY src/ ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN useradd bot

USER bot
CMD ["python3", "-u", "bot.py"]