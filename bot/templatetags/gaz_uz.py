from django import template
from django.http import HttpRequest

from ek import regions

register = template.Library()


@register.filter(name='province')
def province(province_id):
    return regions.get_province(province_id)


@register.filter(name='district')
def district(province_id, district_id):
    return regions.get_district(province_id, district_id)


@register.filter(name='active_users')
def district(request: HttpRequest):
    return int(request.session.get('active_users', False))
