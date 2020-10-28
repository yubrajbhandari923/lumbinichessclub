# lumbinichessclub
``` Code of lumbinichessclub.com.np ```



# Important REQUIREMENTS
* Install Docker to run locally *
* Create a .env files with atleast following variables to use postgres or you may comment out postgres on docker-compose to use sqlite *
```
DB_ENGINE=django.db.backends.postgresql
DB_TYPE=postgres
DB_DATABASE_NAME=lccdb
DB_USER=
DB_PASSWORD=
DB_HOST=db
DB_PORT=5432
DATABASE=postgres

POSTGRES_USER=
POSTGRES_PASSWORD=
```
* Don't Forget to migrate the database *