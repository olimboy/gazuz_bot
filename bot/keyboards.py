from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton
)
from django.conf import settings as config
from ek import regions
from .import lang


def provinces() -> tuple[str, InlineKeyboardMarkup]:
    markup = InlineKeyboardMarkup(row_width=1)
    keyboards = [InlineKeyboardButton(province['name'], callback_data='p_' + province['id']) for province in regions.provinces()]
    markup.add(*keyboards)
    return lang.provinces[config.BOT_LANG], markup


def districts(province_id: str) -> tuple[str, InlineKeyboardMarkup]:
    markup = InlineKeyboardMarkup(row_width=1)
    province, districts = regions.districts(province_id)
    keyboards = [InlineKeyboardButton(district['name'], callback_data='d_' + district['id'] + '_' + province['id']) for district in districts]
    markup.add(*keyboards)
    return province['name'] + '\n' + lang.districts[config.BOT_LANG], markup


def menu(province_id, district_id, account=None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    province_name, district_name = regions.province_and_district_by_id(province_id, district_id)
    markup.add(KeyboardButton(lang.provinces_btn.get(config.BOT_LANG)))
    if province_name != '' and district_name != '':
        markup.add('📍 ' + province_name + ' | ' + district_name)
    if account:
        markup.add('⚡️ ' + province_name + ' | ' + district_name + ' | ' + account)
    return lang.menu.get(config.BOT_LANG), markup