from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
import regions

def provinces() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    keyboards = [InlineKeyboardButton(province['name'], callback_data=str(province['id'])) for province in regions.provinces()]
    markup.add(*keyboards)
    return markup

def districts():
    pass