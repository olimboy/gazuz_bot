from telebot import types
import telebot
import requests
import config
import keyboards
import ek

users = {}

bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.reply_to(message, 'Assalomu alaykum!')
    text, markup = keyboards.provinces()
    bot.reply_to(message, text, reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == 'Viloyatlar')
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
    text = 'Hisob raqamni kiriting:'
    bot.edit_message_text(text, chat_id=msg.chat.id, message_id=msg.id)
    users[msg.chat.id] = district_id, province_id


@bot.message_handler(func=lambda msg: msg.text.count(' | ') == 1)
def check_by_province_and_district_name(message: types.Message):
    text = 'Hisob raqamni kiriting:'
    bot.reply_to(message, text)


@bot.message_handler(func=lambda msg: msg.text.count(' | ') == 2)
def check_by_province_and_district_and_account(message: types.Message):
    district_id, province_id = users[message.chat.id]
    account = message.text.split(' | ')[-1]
    text = ek.check_balance(account, province_id, district_id)
    bot.reply_to(message, text, parse_mode='Markdown')
    text, markup = keyboards.menu(province_id, district_id, account)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.chat.id in users)
def check(message: types.Message):
    district_id, province_id = users[message.chat.id]
    text = ek.check_balance(message.text, province_id, district_id)
    bot.reply_to(message, text, parse_mode='Markdown')
    text, markup = keyboards.menu(province_id, district_id, message.text)
    bot.send_message(message.chat.id, text, reply_markup=markup)


bot.polling(none_stop=True)