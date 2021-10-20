makemigrations:
	docker-compose run --rm web python manage.py makemigrations

migrate:
	docker-compose run --rm web python manage.py migrate

createsuperuser:
	docker-compose run --rm web python manage.py createsuperuser

test:
	docker-compose run --rm web python manage.py test

ssh:
	docker-compose run --rm web bash

pip-compile:
	docker-compose run --rm web sh -c "pip install pip-tools && pip-compile"

# make runserver: only start `db` and `web` by default.
runserver:
	docker-compose up db web

# make runstatic: only needed when you want to make some changes to JS, SCSS or adding other assets.
runstatic:
	docker-compose up static

buildstatic:
	docker-compose run --rm static sh -c "npm install && npm run build"