# multi stages build

# app base
FROM python:3.9-slim-bullseye as base
WORKDIR /app
COPY . ./
RUN pip3 install -r requirements.txt

# development
FROM base as dev
CMD ["python","manage.py","runserver", "0.0.0.0:8000"]

# build static
FROM node:14-slim as staticfiles
WORKDIR /staticfiles
COPY _static/ .
RUN npm install && npm run build

# production
# built to run on Digital Ocean App Platform:
# - DO default port: 8080
# - DO worker temp dir: /dev/shm
FROM base as prod
WORKDIR /app
COPY --from=staticfiles /staticfiles/dist /app/_static/dist
RUN python3 manage.py collectstatic --noinput

ARG app_version
ENV APP_VERSION=${app_version}
ENV APP_WORKERS 3
ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers $APP_WORKERS --worker-tmp-dir=/dev/shm upkoding.wsgi:application
