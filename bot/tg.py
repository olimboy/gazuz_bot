from telebot import types
from django.conf import settings as config
from ek import api, regions
import telebot
from . import keyboards, lang
from bot.models import User
from chatbase import Message

bot = telebot.TeleBot(config.BOT_TOKEN)


def send_analytics(chat_id, msg, user: User):
    intent = "O'zbekiston"

    if user.district_id and user.province_id:
        province = regions.get_province(user.province_id)
        district = regions.get_district(user.province_id, user.district_id)
        intent = f'{province}-{district}'

    message = Message(
        api_key=config.CHATBASE_API_KEY,
        platform='Telegram',
        message=msg,
        intent=intent,
        version='1.0',
        user_id=chat_id,
    )
    message.not_handled = True
    message.set_as_type_user()

    try:
        message.send()
    except:
        pass


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.reply_to(message, lang.hello.get(config.BOT_LANG))
    text, markup = keyboards.provinces()
    bot.reply_to(message, text, reply_markup=markup)
    user, created = User.objects.update_or_create(pk=message.chat.id)
    send_analytics(message.chat.id, message.text, user)


@bot.message_handler(func=lambda msg: msg.text == lang.provinces_btn.get(config.BOT_LANG))
def provinces_by_text(message: types.Message):
    text, markup = keyboards.provinces()
    bot.reply_to(message, text, reply_markup=markup)
    user = User.objects.get(pk=message.chat.id)
    send_analytics(message.chat.id, message.text, user)


@bot.callback_query_handler(func=lambda c: c.data.startswith('p'))
def provinces(callback: types.CallbackQuery):
    province_id = callback.data.replace('p_', '')
    text, markup = keyboards.districts(province_id)
    msg: types.Message = callback.message
    bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.id, reply_markup=markup)
    user = User.objects.get(pk=callback.message.chat.id)
    send_analytics(callback.message.chat.id, callback.message.text, user)


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
    send_analytics(callback.message.chat.id, callback.message.text, user)


@bot.message_handler(func=lambda msg: msg.text and msg.text.count(' | ') == 1)
def check_by_province_and_district_name(message: types.Message):
    text = lang.account_input.get(config.BOT_LANG)
    bot.reply_to(message, text)
    user = User.objects.get(pk=message.chat.id)
    send_analytics(message.chat.id, message.text, user)


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
    send_analytics(message.chat.id, message.text, user)


@bot.message_handler(func=lambda msg: User.objects.filter(pk=msg.chat.id).first())
def check(message: types.Message):
    user = User.objects.get(pk=message.chat.id)
    district_id, province_id = user.district_id, user.province_id
    msg = bot.reply_to(message, lang.loading.get(config.BOT_LANG))
    text = api.check_balance(message.text, province_id, district_id)
    bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.id, parse_mode='Markdown')
    text, markup = keyboards.menu(province_id, district_id, message.text)
    bot.send_message(message.chat.id, text, reply_markup=markup)
    send_analytics(message.chat.id, message.text, user)
