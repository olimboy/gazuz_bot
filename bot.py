from telebot import types
import telebot
import requests
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=['/start'])
def start(message: types.Message):
    bot.reply_to(message, 'Assalomu alaykum!')
