FROM python:3.9-slim-bullseye

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV APP_WORKERS 3
# Digital Ocean default PORT
ENV PORT 8080

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers $APP_WORKERS upkoding.wsgi:application
