from django.contrib import admin
from django.db.models import Count

from bot.models import User, Province, District
from ek import regions


def get_models(qs, group_by):
    print(qs)
    models = []
    for q in qs:
        obj = {'count': q['count'], 'province': regions.get_province(q['province_id'])}
        if group_by == 'district':
            obj['district'] = regions.get_district(q['province_id'], q['district_id'])
        models.append(obj)
    return models


class ProvinceAdminForm(admin.ModelAdmin):
    change_list_template = 'provinces.html'
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
            print(qs.query)
        except (AttributeError, KeyError):
            return response
        response.context_data[self.group_by] = get_models(qs, self.group_by)

        return response


class DistrictAdminForm(ProvinceAdminForm):
    change_list_template = 'districts.html'
    group_by = 'district'
    columns = ('district_id', 'province_id')


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'province_id', 'district_id')


admin.site.register(User, UserAdmin)
admin.site.register(Province, ProvinceAdminForm)
admin.site.register(District, DistrictAdminForm)
