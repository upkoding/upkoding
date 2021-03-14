sqlproxy:
	../cloud_sql_proxy -instances=upkoding:us-central1:upkoding-postgresql=tcp:5432

deploy:
	./manage.py collectstatic --noinput
	gcloud app deploy --project upkoding