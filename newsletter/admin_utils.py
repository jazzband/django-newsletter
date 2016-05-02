from functools import update_wrapper

from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext as _
from .models import Subscription


class ExtendibleModelAdminMixin(object):
    def _getobj(self, request, object_id):
        opts = self.model._meta

        to_field = request.POST.get(
            TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field)

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(
                _('%(name)s object with primary key %(key)r does not exist.') %
                {
                    'name': force_text(opts.verbose_name),
                    'key': escape(object_id)
                }
            )

        return obj

    def _wrap(self, view):
        def wrapper(*args, **kwargs):
            return self.admin_site.admin_view(view)(*args, **kwargs)
        return update_wrapper(wrapper, view)

    def _view_name(self, name):
        info = self.model._meta.app_label, self.model._meta.model_name, name

        return '%s_%s_%s' % info


def make_subscription(newsletter, email, name=None):
    addr = Subscription(subscribed=True)

    addr.newsletter = newsletter
    addr.email_field = email

    if name:
        addr.name_field = name

    return addr
