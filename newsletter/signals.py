import django.dispatch


pre_submit = django.dispatch.Signal()
post_submit = django.dispatch.Signal()

pre_send = django.dispatch.Signal()
post_send = django.dispatch.Signal()
