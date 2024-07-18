PACKAGE_NAME = "django-newsletter"

# importlib is available in python >= 3.8.
# Remove the except importError once support for python < 3.8 is dropped.

try:
    from importlib.metadata import distribution, PackageNotFoundError

    def get_distribution_version():
        try:
            return distribution(PACKAGE_NAME).version
        except PackageNotFoundError:
            # package is not installed
            return None
except ImportError:
    from pkg_resources import get_distribution, DistributionNotFound

    def get_distribution_version():
        try:
            return get_distribution(PACKAGE_NAME).version
        except DistributionNotFound:
            # package is not installed
            return None


__version__ = get_distribution_version()
