from . import ChoiceState, DescriptionState, HardwareChoice, InitialState, SeverityChoice,\
    SoftwareChoice, TitleState, hardware_list, severities_list, software_list, change_state

from hangouts import views
from hangouts.models import User

from vsts.views import create_work_item


class EndState(ChoiceState):
    STATE_LABEL = "end"

    @staticmethod
    def action(message, event):
        user_object = User.objects.get(name=event['space']['name'])
        work_item = user_object.get_work_item()

        user_object.is_finished = True
        user_object.save()

        if message == "save":
            # views.delete_message(event['message']['name'])
            user_object.is_finished = False
            user_object.save()

            path_dict = work_item.path_dict
            fields_dict = views.generate_fields_dict(work_item)

            work_item_dict = {}

            for key, value in path_dict.items():
                work_item_dict[value] = fields_dict[key]

            req = create_work_item(work_item_dict, work_item.url, user_object)
            print(work_item_dict)
            print("req")
            print(req)

            change_state(user_object, InitialState.STATE_LABEL)
            work_item.delete()

            # body = views.generate_work_item(work_item, req['_links']['html']['href'])
            # views.send_message(body, event['space']['name'])


            text_response = views.text_format("Your work item has been saved.")
            card_response = views.generate_work_item(work_item, req['_links']['html']['href'])
            response = [text_response, card_response]

            return response
            # return views.generate_work_item(work_item, req['_links']['html']['href'])

        elif message == "Title":
            user_object.state = TitleState.STATE_LABEL
            user_object.save()

            return views.text_format("Please enter your issue Title.")

        elif message == "Description":
            user_object.state = DescriptionState.STATE_LABEL
            user_object.save()

            return views.text_format("Please describe your issue.")

        elif message == "Hardware Type":
            user_object.state = HardwareChoice.STATE_LABEL
            user_object.save()

            return views.generate_choices("Choose Hardware Type", hardware_list, hardware_choice.HardwareChoice.STATE_LABEL)

        elif message == "Severity":
            user_object.state = SeverityChoice.STATE_LABEL
            user_object.save()

            return views.generate_choices("How severe is this issue?", severities_list, severity_choice.SeverityChoice.STATE_LABEL)

        elif message == "Third Party":
            user_object.state = SoftwareChoice.STATE_LABEL
            user_object.save()

            return views.generate_choices("Choose 3rd Party Software", software_list, software_choice.SoftwareChoice.STATE_LABEL)

    @staticmethod
    def where():
        return "You're near the finish line. Please evaluate your issue at the card above and click" \
               " `save` when you're done."
