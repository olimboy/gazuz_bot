from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import IS_POPUP_VAR, TO_FIELD_VAR
from django.contrib.admin.utils import flatten_fieldsets
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.utils.translation import gettext as _

from bot.models import User, Province, District
from ek import regions


def get_models(qs, group_by):
    models = []
    for q in qs:
        obj = {'count': q['count'], 'province': regions.get_province(q['province_id'])}
        obj.update(dict(q))
        if group_by == 'district':
            obj['district'] = regions.get_district(q['province_id'], q['district_id'])
        models.append(obj)
    return models


class ProvinceAdminForm(admin.ModelAdmin):
    change_list_template = 'provinces.html'
    change_form_template = 'province_districts.html'
    group_by = 'province'
    columns = ('province_id',)

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False

    def has_delete_permission(*args, **kwargs):
        return False

    def get_changelist_instance(self, request):
        """
        Return a `ChangeList` instance based on `request`. May raise
        `IncorrectLookupParameters`.
        """
        self.model = User
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ['action_checkbox', *list_display]
        sortable_by = self.get_sortable_by(request)
        ChangeList = self.get_changelist(request)
        return ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_search_fields(request),
            self.get_list_select_related(request),
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by,
        )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = User._default_manager.get_queryset()
            qs = qs.values(*self.columns).annotate(count=Count(f'{self.group_by}_id')).order_by('-count')
        except (AttributeError, KeyError):
            return response
        response.context_data[self.group_by] = get_models(qs, self.group_by)

        return response

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        self.model = User
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        model = self.model
        opts = model._meta

        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = User._default_manager.get_queryset().first()
            if request.method == 'POST':
                if not self.has_change_permission(request, obj):
                    raise PermissionDenied
            else:
                if not self.has_view_or_change_permission(request, obj):
                    raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request, obj, change=not add, fields=flatten_fieldsets(fieldsets)
        )

        form = ModelForm(instance=obj)
        formsets, inline_instances = self._create_formsets(request, obj, change=True)

        if not add and not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(fieldsets)
        else:
            readonly_fields = self.get_readonly_fields(request, obj)
        adminForm = helpers.AdminForm(
            form,
            list(fieldsets),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            self.get_prepopulated_fields(request, obj) if add or self.has_change_permission(request, obj) else {},
            readonly_fields,
            model_admin=self)
        media = self.media + adminForm.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
        for inline_formset in inline_formsets:
            media = media + inline_formset.media

        if add:
            title = _('Add %s')
        elif self.has_change_permission(request, obj):
            title = _('Change %s')
        else:
            title = _('View %s')
        context = {
            **self.admin_site.each_context(request),
            'title': title % opts.verbose_name,
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            'media': media,
            'inline_admin_formsets': inline_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'preserved_filters': self.get_preserved_filters(request),
        }

        context.update(extra_context or {})
        qs = User._default_manager.get_queryset()
        qs = qs.filter(province_id=object_id).values('district_id', 'province_id').annotate(
            count=Count('district_id')).order_by('-count')

        context.update({'province': regions.get_province(object_id), 'districts': get_models(qs, 'district')})
        return self.render_change_form(request, context, add, False, form_url, obj)


class DistrictAdminForm(ProvinceAdminForm):
    change_list_template = 'districts.html'
    group_by = 'district'
    columns = ('district_id', 'province_id')


admin.site.register(User)
admin.site.register(Province, ProvinceAdminForm)
admin.site.register(District, DistrictAdminForm)
