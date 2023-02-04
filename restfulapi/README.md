# Django App

For the insertion of `commit` records and the querying of possible Owners according to the function

## Start

Run the container and enter it, -e followed by the environment variables, configured as appropriate

`docker run -it -e POSTGRES_DBNAME="whosbug" -e POSTGRES_USER="guest" -e POSTGRES_PASSWORD="guest" -e POSTGRES_HOST="39.101.192.144" -e POSTGRES_PORT="5432" -p 9000:8000 <IMAGE>:<TAG>`

`docker run` is automatically executed `migrate`and`runserver 0.0.0.0:8000`

Create superuser after entering container (optional)

    python3 manage.py createsuperuser

Quit the container and keep it running in the background

    Ctrl + p + q