import json
import config

regions_json = None

with open('regions.json') as f:
    regions_json = f.read()

regions = json.loads(regions_json)

def provinces() -> list:
    provinces = [{'name': province['AreaName'][config.BOT_LANG], 'id': province['Code']} for province in regions]
    return provinces

def districts(province_id: str) -> tuple[dict, list]:
    province = None
    for region in regions:
        if region['Code'] == province_id:
            province = region
            break
    
    districts = [{'name': district['AreaName'][config.BOT_LANG], 'id': district['Code']} for district in province['Children']['Area']]
    province = {'name': province['AreaName'][config.BOT_LANG], 'id': province['Code']}
    
    return province, districts

def province_and_district_by_id(province_id: str, district_id: str) -> tuple[str, str]:
    province = {'AreaName': {config.BOT_LANG: ''}}
    district = {'AreaName': {config.BOT_LANG: ''}}
    for region in regions:
        if region['Code'] == province_id:
            province = region
            for _district in region['Children']['Area']:
                if _district['Code'] == district_id:
                    district = _district
                    break
            break
    return province['AreaName'][config.BOT_LANG], district['AreaName'][config.BOT_LANG]

def province_and_district_by_name(province_name: str, district_name: str) -> tuple[str, str]:
    province = {'Code': None}
    district = {'Code': None}
    for region in regions:
        if region['AreaName'][config.BOT_LANG] == province_name:
            province = region
            for _district in region['Children']['Area']:
                if _district['AreaName'][config.BOT_LANG] == district_name:
                    district = _district
                    break
            break
    return province['Code'], district['Code']