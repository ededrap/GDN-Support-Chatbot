# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .states import *
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from hangouts.models import User, HardwareSupport, SoftwareSupport
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

import vsts.views

import json

HANGOUTS_CHAT_API_TOKEN = 'SuCgaoGMzcA-U5xymm8khOEEezAapfV9fj5r2U3Tcjw='


# ----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(payload):
    event = json.loads(payload.body)
    print(event)
    if event['token'] == HANGOUTS_CHAT_API_TOKEN:
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
            if state.is_waiting_text():
                response = globals()[state.label()](message, event)
            else:
                response = text_format("Please complete above Card action first")

        elif event['type'] == 'CARD_CLICKED':
            response = handle_action(event)
            if not state.is_waiting_text():
                # response can be text or card, depending on action
                response = handle_action(event)
        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')


def initial_state(message, event):
    if message.lower() == 'support':
        response = generate_choices("Choose work item type", ["Hardware Support", "Software Support"], "choose_type")
        change_state(event['space']['name'])
    else:
        message = 'You said: `%s`' % message
        response = text_format(message)

    return response


def text_format(message):
    return {"text": message}


def handle_action(event):
    action = event['action']
    if action['actionMethodName'] == "choose_type":
        chosen = work_item_choice(action['parameters'][0]['value'], event['space'])
        response = text_format("You have chosen '%s'\nPlease enter title" % chosen)
    elif action['actionMethodName'] == "save_work_item":
        response = save_work_item(event)
    elif action['actionMethodName'] == "edit_work_item":
        response = text_format("Belum bisa")
    elif action['actionMethodName'] == "3rd_party_app":
        return
    else:
        return

    change_state(event['space']['name'])
    return response


# ----------------------- create work item -----------------------#
def work_item_choice(item_type, space):
    user_object = User.objects.get(name=space['name'])
    if item_type == 'Hardware Support':
        work_item_object = HardwareSupport.objects.create()
    elif item_type == 'Software Support':
        work_item_object = SoftwareSupport.objects.create()

    user_object.work_item = work_item_object
    user_object.save()
    return item_type


def set_title(message, event):
    user_object, created = User.objects.get_or_create(name=event['space']['name'])

    work_item = user_object.work_item
    work_item.title = message
    work_item.save()

    change_state(event['space']['name'])
    # hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
    # response = generate_choices("Choose Hardware Type", hardware_type, "hardware_type")

    return text_format("Please enter description")


def set_description(message, event):
    user_object, created = User.objects.get_or_create(name=event['space']['name'])

    work_item = user_object.work_item
    work_item.description = message
    work_item.save()

    change_state(event['space']['name'])

    return generate_edit_work_item(work_item)

def save_work_item(event):
    user_object, created = User.objects.get_or_create(name=event['space']['name'])
    work_item = user_object.work_item
    path_dict = work_item.path_dict
    fields_dict = generate_fields_dict(work_item)

    work_item_dict = {}

    for key, value in path_dict.items():
        work_item_dict[value] = fields_dict[key]

    # vsts.views.create_work_item(work_item_dict)
    print(work_item_dict)
    return text_format("Your work item has been saved.")

def generate_fields_dict(work_item):
    dict = model_to_dict(work_item)
    del dict["id"]

    return dict

# ----------------------- send message asynchronously -----------------------#
def send_message(body, space):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'project-id-2458129994854391868-7fe6d3521132.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(parent=space, body=body).execute()

    print(resp)


# ----------------------- card generators -----------------------#
def generate_choices(title, list, method):
    if list == [] and method == 'unsubscribe':
        return text_format("You did not subscribe to any area.")

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

    for item in list:
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
    dict = generate_fields_dict(work_item)
    for old_key in dict.keys():
        new_key = old_key.replace("_", " ").title()
        dict[new_key] = dict.pop(old_key)

    card = {
        "cards": [
            {
                "header": {
                    "title": work_item.title,
                    "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/WMF-Agora-Settings_808080.svg/1024px-WMF-Agora-Settings_808080.svg.png"
                },
                "sections": [
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


    for label, content in dict.items():
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

        card['cards'][0]['sections'][0]['widgets'].append(item_widget)

    return card

def generate_bug(message):
    card = {
      "cards": [
        {
          "header": {
            "title": message['fields']['System.Title'],
            "subtitle": "created by " + message['fields']['System.CreatedBy'],
            "imageUrl": "https://www.iconspng.com/uploads/bad-bug/bad-bug.png"
          },
          "sections": [
            {
              "widgets": [
                  {
                    "keyValue": {
                        "topLabel": "Area Path",
                        "content": message['fields']['System.AreaPath'],
                    }
                  },
                  {
                    "keyValue": {
                        "topLabel": "Severity",
                        "content": message['fields']['Microsoft.VSTS.Common.Severity'],
                    }
                  },
                  {
                    "keyValue": {
                        "topLabel": "Repro Steps",
                        "content": message['fields']['Microsoft.VSTS.TCM.ReproSteps'],
                    }
                  }
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
                                "url": message['_links']['html']['href']
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