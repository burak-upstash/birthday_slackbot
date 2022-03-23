from chalice import Chalice, Cron, Rate
import os
from datetime import date
from chalicelib.utils import responseToDict, postToChannel
from chalicelib.upstash import fetchFromUpstash, setEvent, getEvent, getAllEvents, removeEvent

app = Chalice(app_name='birthday-slackbot')

print(getAllEvents())

@app.route('/', methods=["GET"])
def something():
    return {
        "Hello": "World"
        }


@app.route('/', methods=["POST"], content_types=["application/x-www-form-urlencoded"])
def index():
    r = responseToDict(app.current_request.raw_body)

    # command = r['command']
    
    # command parameters will be splitted via commas (",")
    commandArray = r['text'].split(",")
    command = commandArray[0]

    commandArray.pop(0)

    if command == "set":
        setEvent(commandArray)
    elif command == "get":
        stringResult = getEvent(commandArray)
        return {
        'response_type': "ephemeral",
        'text': "Event Details:\n\n {}".format(stringResult)
        }

    elif command == "get-all":
        stringResult = getAllEvents()
        return {
        'response_type': "ephemeral",
        'text': "All events: {}".format(stringResult)
        }

    elif command == "remove":
        removeEvent(commandArray)
    else:
        return {
        'response_type': "ephemeral",
        'text': "Usage: `<command>, <event-info>, <MM-DD>, any additional_info as string`, <> represent strings without spaces"
        }


    # resultPostChannel = postToChannel('general', 'testing func...')

    return {
        # Ephemeral since it is a suprise!
        'response_type': "ephemeral",
        'text': "splitted: {}".format(commandArray)
        # 'text': "splitted: {}, {}".format(commandArray, res)
        # 'text': """Command: {}, parameters: {}.""".format(r['command'], resultPostChannel['message']['text'])
        }


# Run at 10:00 am (UTC) every day.
@app.schedule(Cron(0, 10, '*', '*', '?', '*'))
def periodicCheck(event):
    # Cron job calls this function.
    # This is where the alert system etc will take place.
    
    # fetch data from Upstash
    fetchFromUpstash()
    
    # see whether there are any birthdays/events coming,
    # notify people.
    # DM everyone - the relevant person
    
    # notifyPeople()

    # If the day came, than publish a message to general channel
    # Or any channel you like...
    postToChannel('general', 'This works I hope...')

@app.schedule(Rate(30, unit=Rate.MINUTES))
def periodic_task(event):
    print("Cron 2...")
    postToChannel('general', 'Cron 2')



