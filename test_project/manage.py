#!/usr/bin/env python
import os
import sys
import pathlib

import dotenv

root = pathlib.Path(__file__).parent.parent

if __name__ == "__main__":
    dotenv.read_dotenv(str(root / ".env"))

    sys.path.append(str(root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
