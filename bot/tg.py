from telebot import types
from django.conf import settings as config
from ek import api
import telebot
from .import keyboards, lang
from bot.models import User

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.reply_to(message, lang.hello.get(config.BOT_LANG))
    text, markup = keyboards.provinces()
    bot.reply_to(message, text, reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == lang.provinces_btn.get(config.BOT_LANG))
def provinces_by_text(message: types.Message):
    text, markup = keyboards.provinces()
    bot.reply_to(message, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('p'))
def provinces(callback: types.CallbackQuery):
    province_id = callback.data.replace('p_', '')
    text, markup = keyboards.districts(province_id)
    msg: types.Message = callback.message
    bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith('d'))
def districts(callback: types.CallbackQuery):
    district_id, province_id = callback.data.split('_')[1:]
    msg: types.Message = callback.message
    text = lang.account_input.get(config.BOT_LANG)
    bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.id)
    user, created = User.objects.update_or_create(pk=msg.chat.id)
    user.district_id = district_id
    user.province_id = province_id
    user.save()


@bot.message_handler(func=lambda msg: msg.text and msg.text.count(' | ') == 1)
def check_by_province_and_district_name(message: types.Message):
    text = lang.account_input.get(config.BOT_LANG)
    bot.reply_to(message, text)


@bot.message_handler(func=lambda msg: msg.text and msg.text.count(' | ') == 2)
def check_by_province_and_district_and_account(message: types.Message):
    user = User.objects.get(pk=message.chat.id)
    district_id, province_id = user.district_id, user.province_id
    account = message.text.split(' | ')[-1]
    msg = bot.reply_to(message, lang.loading.get(config.BOT_LANG))
    text = api.check_balance(account, province_id, district_id)
    bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.id, parse_mode='Markdown')
    text, markup = keyboards.menu(province_id, district_id, account)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda msg: User.objects.filter(pk=msg.chat.id).first())
def check(message: types.Message):
    user = User.objects.get(pk=message.chat.id)
    district_id, province_id = user.district_id, user.province_id
    msg = bot.reply_to(message, lang.loading.get(config.BOT_LANG))
    text = api.check_balance(message.text, province_id, district_id)
    bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.id, parse_mode='Markdown')
    text, markup = keyboards.menu(province_id, district_id, message.text)
    bot.send_message(message.chat.id, text, reply_markup=markup)
