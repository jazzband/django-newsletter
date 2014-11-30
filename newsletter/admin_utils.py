from django.http import Http404

from functools import update_wrapper
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin.util import unquote
from django.utils.encoding import force_unicode


class ExtendibleModelAdminMixin(object):
    def _getobj(self, request, object_id):
            opts = self.model._meta

            try:
                obj = self.queryset(request).get(pk=unquote(object_id))
            except self.model.DoesNotExist:
                # Don't raise Http404 just yet, because we haven't checked
                # permissions yet. We don't want an unauthenticated user to
                # be able to determine whether a given object exists.
                obj = None

            if obj is None:
                raise Http404(
                    _(
                        '%(name)s object with primary key '
                        '%(key)r does not exist.'
                    ) % {
                        'name': force_unicode(opts.verbose_name),
                        'key': unicode(object_id)
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
