## To run project


### run the below in a terminal in the dir you want to save the project;

```
pip3 install pipenv
git clone https://github.com/Blindrabit/graphql-booking-app.git
```
### open the project in an ide and run the below

```
pipenv install && pipenv shell
```

### create an .env file
```
touch .env
```

### add the below to the .env file - feel free to add your own secret key;

```
DJANGO_SECRET_KEY=django-insecure-ADD-YOUR-OWN-SECRET-KEY
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1
```

### run in your terminal
```
python3 manage.py migrate 
```
### to add dummy data

```
python3 manage.py loaddata fixtures/office.json
python3 manage.py loaddata fixtures/users.json
python3 manage.py loaddata fixtures/bookings.json
```
### to run the server

```
python3 manage.py runserver
```
