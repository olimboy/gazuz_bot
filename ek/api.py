from requests import Session
from bs4 import BeautifulSoup
from django.conf import settings as config


def check_balance(account, province_id, district_id):
    ses = Session()
    res = ses.get(config.EK_URL)
    soup = BeautifulSoup(res.text, 'lxml')
    csrf = soup.find('meta', {"name": "csrf-token"}).get('content')
    data = {
        '_csrf': csrf,
        'Balance[personal_account]': account,
        'Balance[service_id]': "3",
        'Balance[region_id]': province_id,
        'Balance[sub_region_id]': district_id
    }
    res = ses.post(config.EK_URL, data)
    # with open('temp.html', 'w', encoding='utf-8') as f:
    #     f.write(res.text)
    result = ''
    tbl = BeautifulSoup(res.text, 'lxml').find('table')
    if not tbl:
        return "*Ma'lumot topilmadi. Ehtimol hisob raqamni xato kiritdingiz!*"
    for tr in tbl.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) > 0:
            result += '\n*' + tds[0].text + '*: ' + ' '.join(map(lambda td: '_' + str(td.text).strip() + '_', tds[1:]))
    
    return result