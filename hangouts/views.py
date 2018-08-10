# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .cards import text_format
from .models import User
from .states.states import InitialState, states_list, change_state

from django.conf import settings

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from googleapiclient.discovery import build

import json

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials


# ----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(payload):
    event = json.loads(payload.body)
    print(event)
    if event['token'] == settings.HANGOUTS_CHAT_API_TOKEN:
        user_object, created = User.objects.get_or_create(name=event['space']['name'])
        state = states_list[user_object.state]
        if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
            message = 'Thanks for adding me to "%s"!' % event['space']['displayName']
            response = text_format(message)

        elif event['type'] == 'MESSAGE':
            # room or direct message
            if event['space']['type'] == 'ROOM':
                message = event['message']['argumentText'][1:]
            else:
                message = event['message']['argumentText']
            if message == '/help':
                response = text_format('Type `support` to start issuing new Work Item!\n\n'
                                       + 'Type `/where` to know where you are on issuing a new Work Item\n'
                                       + 'Type `/reset` to abort all progress on issuing a new Work Item')
            elif message == '/reset':
                user_object.is_finished = False
                user_object.save()

                change_state(user_object, InitialState.STATE_LABEL)

                try:
                    user_object.work_item.delete()
                except AttributeError:
                    pass

                response = text_format("Your progress has been aborted")
            elif message == '/where':
                response = text_format(state.where())
                response["actionResponse"] = {"type": "UPDATE_MESSAGE"}
            elif state.is_waiting_text():
                response = state.action(user_object, message, event)
            else:
                response = text_format(state.where())

        elif event['type'] == 'CARD_CLICKED':
            if not state.is_waiting_text():
                # response can be text or card, depending on action
                action = event['action']
                if action['actionMethodName'] == state.STATE_LABEL:
                    response = state.action(user_object, action['parameters'][0]['value'], event)
                else:
                    response = text_format(state.where())
            else:
                response = text_format(state.where())
        else:
            return
    else:
        return

    # response['thread'] = {"name": event['message']['thread']['name']}
    # print("thread")
    # print(event['message']['thread']['name'])
    print(response)
    # send_message(response, event['space']['name'])
    return JsonResponse(response, content_type='application/json')


# ----------------------- send message asynchronously -----------------------#
def send_message(body, user):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'GDN Support Bot service key.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(parent=user, body=body).execute()

    print(resp)


def delete_message(name):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'GDN Support Bot service key.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().delete(name=name).execute()

    print(resp)