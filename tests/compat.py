import sys
from typing import Generator

if sys.version_info < (3, 7):
    from contextlib import contextmanager

    @contextmanager
    def nullcontext() -> Generator:
        yield


else:
    from contextlib import nullcontext  # noqa: F401
