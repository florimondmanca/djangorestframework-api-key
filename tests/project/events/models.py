from django.db import models

CODE = "publish"
NAME = "Can publish an event"
CODE_TOO_LONG = CODE * 10
NAME_TOO_LONG = NAME * 10
DUPLICATE_CODE = CODE
CLASHING_CODE = "create"


class Event(models.Model):
    class Meta:
        verbose_name = "Event" * 20
        api_key_scopes = [
            (CODE_TOO_LONG, NAME),
            (CODE, NAME_TOO_LONG),
            (DUPLICATE_CODE, NAME),
            (CLASHING_CODE, NAME),
        ]
