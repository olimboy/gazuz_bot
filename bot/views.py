from django.shortcuts import render
from django.conf import settings as config
from django.http import HttpRequest, HttpResponseForbidden, HttpResponse
from telebot import types
from .tg import bot
from django.conf import settings as config

print('Bot Listen Type:', config.BOT_LISTEN_TYPE)

if config.BOT_LISTEN_TYPE == 'webhook':
    bot.set_webhook(config.BOT_WEBHOOK_URL)
else:
    bot.infinity_polling()

def webhook(request: HttpRequest):
    if request.method == 'POST' and request.content_type == 'application/json':
        json_string = request.body.decode("utf-8")
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse()
    return HttpResponseForbidden()
