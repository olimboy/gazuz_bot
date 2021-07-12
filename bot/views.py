import json
import sys
from threading import Thread

from django.conf import settings as config
from django.http import HttpRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from telebot import types

from .models import User
from .tg import bot

if 'runserver' in sys.argv:
    print('Bot Listen Type:', config.BOT_LISTEN_TYPE)
    if config.BOT_LISTEN_TYPE == 'webhook':
        bot.set_webhook(config.BOT_WEBHOOK_URL)
    elif config.BOT_LISTEN_TYPE == 'polling':
        bot.remove_webhook()
        Thread(target=bot.infinity_polling).start()


@csrf_exempt
def webhook(request: HttpRequest):
    if request.method == 'POST' and request.content_type == 'application/json':
        json_string = request.body.decode("utf-8")
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse()
    return HttpResponseForbidden()


@csrf_exempt
def active(request: HttpRequest, pk):
    User.objects.filter()
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST' and request.content_type == 'application/json':
        json_string = request.body.decode("utf-8")
        data = json.loads(json_string)
        user.active = data['active']
        user.save()
        return HttpResponse()
    return HttpResponseForbidden()


def active_users(request):
    request.session['active_users'] = not request.session.get('active_users', False)
    return redirect(request.headers.get('Referer', '/admin'))