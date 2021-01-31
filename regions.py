import json
import config

regions_json = None

with open('regions.json') as f:
    regions_json =  f.read()

regions = json.loads(regions_json)

def provinces() -> list:
    provinces = [{'name': province['AreaName'][config.BOT_LANG], 'id': province['Id']} for province in regions]
    return provinces

def districts(province_id: int) -> tuple[dict, list]:
    province = None
    for region in regions:
        if region['Id'] == province_id:
            province = region
            break
    
    districts = [{'name': district['AreaName'][config.BOT_LANG], 'id': district['Id']} for district in province['Children']['Area']]
    province = {'name': province['AreaName'][config.BOT_LANG], 'id': province['Id']}
    
    return province, districts
