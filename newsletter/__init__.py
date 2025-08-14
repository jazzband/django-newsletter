from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("django-newsletter")
except PackageNotFoundError:
    # package is not installed
    __version__ = None
