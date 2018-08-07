# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from hangouts.models import User

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

import hangouts.states.states_conf as states_conf
import hangouts.states.initial_state as initial_state
import json


# ----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(payload):
    event = json.loads(payload.body)
    print(event)
    if event['token'] == settings.HANGOUTS_CHAT_API_TOKEN:
        user_object, created = User.objects.get_or_create(name=event['space']['name'])
        state = states_conf.states_list[user_object.state]
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

                states_conf.change_state(user_object, initial_state.InitialState.STATE_LABEL)

                try:
                    user_object.work_item.delete()
                except AttributeError:
                    pass

                response = text_format("Your progress has been aborted")
            elif message == '/where':
                response = text_format(state.where())
            elif state.is_waiting_text():
                response = state.action(message, event)
            else:
                response = text_format(state.where())

        elif event['type'] == 'CARD_CLICKED':
            if not state.is_waiting_text():
                # response can be text or card, depending on action
                action = event['action']
                response = state.action(action['parameters'][0]['value'], event)
            else:
                response = {}
        else:
            return
    else:
        return

    # response['threadKey'] = {"name": event['message']['thread']['name']}
    print("thread")
    print(event['message']['thread']['name'])
    # print(response)
    send_message(response, event)
    return HttpResponse("OK")


def text_format(message):
    return {"text": message}


# ----------------------- send message asynchronously -----------------------#
def send_message(body, event):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'GDN Support Bot service key.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(parent=event['space']['name'], body=body, threadKey=event['message']['thread']['name']).execute()

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


# ----------------------- card generators -----------------------#
def generate_choices(title, choices, method):
    card = {
        "cards": [
            {
                "header": {
                    "title": title
                },
                "sections": [
                    {
                        "widgets": [
                        ]
                    }
                ]
            }
        ]
    }

    for item in choices:
        item_widget = {
            "keyValue": {
                "content": item,
                "onClick": {
                    "action": {
                        "actionMethodName": method,
                        "parameters": [
                            {
                                "key": "param",
                                "value": item
                            }
                        ]
                    }
                }
            }
        }

        card['cards'][0]['sections'][0]['widgets'].append(item_widget)

    return card


def generate_edit_work_item(work_item):
    temp_dict = generate_fields_dict(work_item)

    del temp_dict["title"]
    if "requested_by" in temp_dict:
        del temp_dict["requested_by"]

    work_item_dict = {}

    for old_key in temp_dict.keys():
        new_key = old_key.replace("_", " ").title()
        work_item_dict[new_key] = temp_dict[old_key]

    card = {
        "cards": [
            {
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "content": work_item.title,
                                    "iconUrl": "http://hangouts-vsts.herokuapp.com" +
                                               static('png/' + work_item.url + '.png'),
                                    "button": {
                                        "textButton": {
                                            "text": "Edit",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "edit_work_item",
                                                    "parameters": [
                                                        {
                                                            "key": "field",
                                                            "value": "Title"
                                                        }
                                                    ]
                                                }
                                            }

                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "widgets": [
                        ]
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "SAVE",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "save_work_item",
                                                    "parameters": [
                                                        {
                                                            "key": "field",
                                                            "value": "save"
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    for label, content in work_item_dict.items():
        item_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content,
                "button": {
                    "textButton": {
                        "text": "Edit",
                        "onClick": {
                            "action": {
                                "actionMethodName": "edit_work_item",
                                "parameters": [
                                    {
                                        "key": "field",
                                        "value": label
                                    }
                                ]
                            }
                        }

                    }
                }
            }
        }

        card['cards'][0]['sections'][1]['widgets'].append(item_widget)

    return card

def generate_work_item(work_item):
    temp_dict = generate_fields_dict(work_item)

    del temp_dict["title"]
    if "requested_by" in temp_dict:
        del temp_dict["requested_by"]

    work_item_dict = {}

    for old_key in temp_dict.keys():
        new_key = old_key.replace("_", " ").title()
        work_item_dict[new_key] = temp_dict[old_key]

    card = {
        "cards": [
            {
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "content": work_item.title,
                                    "iconUrl": "http://hangouts-vsts.herokuapp.com" +
                                               static('png/' + work_item.url + '.png'),                                }
                            }
                        ]
                    },
                    {
                        "widgets": [
                        ]
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "MORE",
                                            "onClick": {
                                                "openLink": {
                                                    "url": work_item['_links']['html']['href']
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    for label, content in work_item_dict.items():
        item_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content,
            }
        }

        card['cards'][0]['sections'][1]['widgets'].append(item_widget)

    return card


def generate_updated_work_item(work_item):

    fields = {'Revised by': work_item['revisedBy']['name']}

    if 'System.State' in work_item['fields']:
        fields['State'] = work_item['fields']['System.State']['oldValue'] + \
                          ' --> ' + work_item['fields']['System.State']['newValue']

    if 'System.History' in work_item['fields']:
        fields['Comment'] = work_item['fields']['System.History']['newValue']

    image_url = "http://hangouts-vsts.herokuapp.com" + static('png/' +
                            work_item['revision']['fields']['System.WorkItemType'].replace(" ", "%20") + '.png')

    card = {
        "cards": [
            {
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "content": work_item['revision']['fields']['System.Title'],
                                    "iconUrl": image_url
                                }
                            }
                        ]
                    },
                    {
                        "widgets": [
                        ]
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "MORE",
                                            "onClick": {
                                                "openLink": {
                                                    "url": work_item['_links']['html']['href']
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    for label, content in fields.items():
        item_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content
            }
        }

        card['cards'][0]['sections'][1]['widgets'].append(item_widget)

    return card


def generate_signin_card(user):
    signin_url = "app.vssps.visualstudio.com/oauth2/authorize?client_id=C8A33DD9-D575-428F-A0CA-7210BC9A4363&response_" \
                "type=Assertion&state=" + str(user.pk) + "&scope=vso.work_full&redirect_uri=https://hangouts-vsts.herokuapp.com/vsts/oauth"
    card = {
        "cards": [
            {
                "header": {
                    "title": "Please sign in to your VSTS account."
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "SIGN IN",
                                            "onClick": {
                                                "openLink": {
                                                    "url": signin_url
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    return card


def generate_fields_dict(work_item):
    dict = model_to_dict(work_item)

    del dict["id"]
    del dict["workitem_ptr"]

    return dict
