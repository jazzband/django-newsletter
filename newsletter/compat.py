from django import get_version

if get_version() < '1.10':
    from django.template import Context

def get_context(dictionary, **kwargs):
    """Takes a dict and returns the correct object for template rendering."""
    if get_version() < '1.10':
        return Context(dictionary, **kwargs)
    else:
        return dictionary
