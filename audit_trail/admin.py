from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from audit_trail.models import ContentType, Entity, Xaction
from audit_trail.queries import get_audit_qs


class AuditTrailAdmin(admin.ModelAdmin):

    def audit_col(self, obj):
        opts = self.model._meta
        app_label = opts.app_label
        model_name = opts.model_name
        history_url = reverse('admin:' + app_label + '_' + model_name + '_history',
                              args=(obj.id,))
        return render_to_string('audit_trail/admin_cl_icon.html',
                                {'history_url': history_url})

    audit_col.allow_tags = True
    audit_col.short_description = _('History')

    def history_view(self, request, object_id, extra_context=None):
        model = self.model
        obj = self.get_object(request, unquote(object_id))

        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, model._meta, object_id)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        opts = model._meta
        app_label = opts.app_label
        action_list = get_audit_qs(model._meta.model_name, object_id)
        page = request.GET.get('page', 1)
        page_obj = Paginator(action_list, self.list_per_page).page(page)
        page_obj.object_list = page_obj.object_list. \
            values('transacted_on', 'transacted_by',
                   'transaction_type', 'field_name',
                   'current_val', 'current_val_type',
                   'previous_val', 'previous_val_type',
                   'xaction__display_text'
                   )

        context = dict(
            self.admin_site.each_context(request),
            title=_('Change History: %s' % force_text(obj)),
            action_list=page_obj,
            module_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,
            preserved_filters=self.get_preserved_filters(request),
        )
        context.update(extra_context or {})

        request.current_app = self.admin_site.name

        return TemplateResponse(request, 'audit_trail/history.html', context)


@admin.register(Xaction)
class XactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'entity', 'xaction_type',
        'display_text', 'pfield_val',
        'ts', 'user',
    )
    list_filter = ('xaction_type', 'entity', 'ts')
    search_fields = ('entity__entity_name', 'display_text', 'user__email')


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ('type',)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'primary_field', 'display_format', 'status')
    search_fields = ('entity_name',)
