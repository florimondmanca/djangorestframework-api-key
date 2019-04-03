# djangorestframework-api-key-example

Example project showcasing the usage of [djangorestframework-api-key](../).

This is a pets management app. The API is protected using the `HasAPIKey` permission class.

## Install

- Clone the repo and install dependencies (preferrably in a virtualenv!):

```bash
$ pip install -r requirements.txt
```

- Then run migrations (creates an SQLite database):

```bash
$ python manage.py migrate
```

- Create a superuser to access the admin site:

```bash
$ python manage.py createsuperuser
# Enter user information as instructed
```

- Finally, start the server:

```bash
$ python manage.py runserver
```

## Usage

- Go to the admin site at http://localhost:8000/admin and create an API key:

![](media/admin-section.png)

![](media/admin-form.png)

- The generated API key is shown to you:

![](media/admin-created.png)

- Save it to an environment variable:

```bash
export API_KEY="<The generated API key here>"
```

- Now, create a few pets:

![](media/pets.png)

- Finally, perform some requests to the API! We're using [requests](http://docs.python-requests.org) here:

```python
import os
import requests

url = 'http://localhost:8000/pets/'
resp = requests.get(url)
assert resp.status_code == 403

api_key = os.getenv("API_KEY")
auth = f"Api-Key {api_key}"

resp = requests.get(url, headers={"Authorization": auth})
assert resp.status_code == 200

print(resp.json())
```

Here's the result:

```json
[
  { "id": 1, "animal": "DOG", "nickname": "Jerry" },
  { "id": 2, "animal": "CAT", "nickname": "Suzy" }
]
```

🎉
