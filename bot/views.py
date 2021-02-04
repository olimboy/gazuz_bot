from django.shortcuts import render
from django.conf import settings as config
from django.http import HttpRequest, HttpResponseForbidden, HttpResponse
from telebot import types
from .tg import bot
from django.conf import settings as config
from threading import Thread
from django.views.decorators.csrf import csrf_exempt
import sys

if 'runserver' in sys.argv:
    print('Bot Listen Type:', config.BOT_LISTEN_TYPE)
    if config.BOT_LISTEN_TYPE == 'webhook':
        bot.set_webhook(config.BOT_WEBHOOK_URL)
    else:
        Thread(target=bot.infinity_polling).start()

@csrf_exempt
def webhook(request: HttpRequest):
    if request.method == 'POST' and request.content_type == 'application/json':
        json_string = request.body.decode("utf-8")
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse()
    return HttpResponseForbidden()
