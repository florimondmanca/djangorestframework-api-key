# project

Test project for `djangorestframework-api-key`.

## Usage

- Install dependencies:

```bash
pip install django djangorestframework
pip install -e ../
```

- Run migrations (creates an SQLite database):

```bash
python manage.py migrate
```

- Create a superuser to access the admin site:

```bash
python manage.py createsuperuser
# Enter user information as instructed
```

- Start the server:

```bash
python manage.py runserver
```
