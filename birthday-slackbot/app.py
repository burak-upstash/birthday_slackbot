from chalice import Chalice, Cron, Rate
import os

from chalicelib.utils import responseToDict, parseString, postToChannel
from chalicelib.upstash import postToUpstash, fetchFromUpstash

app = Chalice(app_name='birthday-slackbot')


@app.route('/', methods=["GET"])
def something():
    return {
        "Hello": "World"
        }


@app.route('/', methods=["POST"], content_types=["application/x-www-form-urlencoded"])
def index():
    r = responseToDict(app.current_request.raw_body)

    command = r['command']
    stringArray = parseString(r['text'])

    resultUpstash = postToUpstash(stringArray)
    print("Result from Upstash post:", resultUpstash['result'])

    resultPostChannel = postToChannel('general', 'testing func...')

    return {
        'response_type': "ephemeral",
        'text': """Command: {}, parameters: {}.""".format(r['command'], resultPostChannel['message']['text'])
        }


# Run at 10:00 am (UTC) every day.
@app.schedule(Cron(0, 10, '*', '*', '?', '*'))
# @app.schedule(Cron('*', '*', '*', '*', '?', '*'))
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



