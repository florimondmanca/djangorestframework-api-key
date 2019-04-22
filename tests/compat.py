import sys

if sys.version_info < (3, 7):
    from contextlib import contextmanager

    @contextmanager
    def nullcontext():
        yield


else:
    from contextlib import nullcontext  # pylint: disable=unused-import
