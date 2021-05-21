import json
from pathlib import Path
from django.conf import settings as config

dir = Path(__file__).resolve().parent
regions_json = None

with open(dir / 'regions.json') as f:
    regions_json = f.read()

regions = json.loads(regions_json)


def get_province(province_id: str) -> str:
    province = {'AreaName': {'uz': ''}}
    for region in regions:
        if region['Code'] == province_id:
            province = region
            break
    return province['AreaName']['uz']


def get_district(province_id, district_id) -> str:
    district = {'AreaName': {'uz': ''}}
    for region in regions:
        if region['Code'] == province_id:
            for _district in region['Children']['Area']:
                if _district['Code'] == district_id:
                    district = _district
                    break
            break
    return district['AreaName']['uz']


def provinces() -> list:
    provinces = [{'name': province['AreaName']['uz'], 'id': province['Code']} for province in regions]
    return provinces


def districts(province_id: str) -> tuple[dict, list]:
    province = None
    for region in regions:
        if region['Code'] == province_id:
            province = region
            break

    districts = [{'name': district['AreaName']['uz'], 'id': district['Code']} for district in
                 province['Children']['Area']]
    province = {'name': province['AreaName']['uz'], 'id': province['Code']}

    return province, districts


def province_and_district_by_id(province_id: str, district_id: str) -> tuple[str, str]:
    province = {'AreaName': {'uz': ''}}
    district = {'AreaName': {'uz': ''}}
    for region in regions:
        if region['Code'] == province_id:
            province = region
            for _district in region['Children']['Area']:
                if _district['Code'] == district_id:
                    district = _district
                    break
            break
    return province['AreaName']['uz'], district['AreaName']['uz']


def province_and_district_by_name(province_name: str, district_name: str) -> tuple[str, str]:
    province = {'Code': None}
    district = {'Code': None}
    for region in regions:
        if region['AreaName']['uz'] == province_name:
            province = region
            for _district in region['Children']['Area']:
                if _district['AreaName']['uz'] == district_name:
                    district = _district
                    break
            break
    return province['Code'], district['Code']
