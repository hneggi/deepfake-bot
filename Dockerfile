FROM python:3.6

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
EXPOSE 3306

CMD [ "python", "bot.py" ]
