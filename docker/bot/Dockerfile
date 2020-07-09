FROM python:3.7-slim

WORKDIR /usr/src/app
COPY src/ ./
RUN pip3 install --no-cache-dir -r requirements.txt

USER bot
CMD ["python3", "-u", "bot.py"]