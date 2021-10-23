# multi stages build

# build static
FROM node:14-slim as static_builder
WORKDIR /static_builder
COPY ./_static/ ./
RUN npm install && npm run build

# app base
FROM python:3.9-slim-bullseye as base
WORKDIR /app
COPY . ./
RUN pip3 install -r requirements.txt

# development
FROM base as dev
CMD ["python","manage.py","runserver", "0.0.0.0:8000"]

# production
FROM base as prod
COPY --from=static_builder /static_builder/dist ./_static/
RUN python3 manage.py collectstatic --noinput

ARG app_version
ENV APP_VERSION=${app_version}
ENV APP_WORKERS 3
ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers $APP_WORKERS upkoding.wsgi:application
