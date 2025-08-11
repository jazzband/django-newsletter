from importlib.metadata import distribution, PackageNotFoundError

try:
    __version__ = distribution("django-newsletter").version
except PackageNotFoundError:
    __version__ = None
