import re


class NewsletterActionsConverter:
    regex = '(subscribe|update|unsubscribe)'

    def to_python(self, value):
        result = re.match(self.regex, value)
        return result.group() if result is not None else ''

    def to_url(self, value):
        result = re.match(self.regex, value)
        return result.group() if result is not None else ''
