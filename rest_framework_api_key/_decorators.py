class DjangoProperty(property):
    def __init__(self, fget):
        super().__init__(fget=fget)
        self.name = None

    def __set_name__(self, owner, name):
        setattr(owner, name + "_func", self.fget)


def djangoproperty(**kwargs):
    """A Django admin-friendly variant of @property."""

    def decorate(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        return DjangoProperty(func)

    return decorate
