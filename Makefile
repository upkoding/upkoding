makemigrations:
	docker-compose run web python manage.py makemigrations

migrate:
	docker-compose run web python manage.py migrate

createsuperuser:
	docker-compose run web python manage.py createsuperuser

test:
	docker-compose run web python manage.py test

ssh:
	docker-compose run web bash

runserver:
	docker-compose up