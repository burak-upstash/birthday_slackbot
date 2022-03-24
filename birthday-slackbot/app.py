from chalice import Chalice, Cron, Rate
import os
from datetime import date
from chalicelib.utils import responseToDict, postToChannel, diffWithTodayFromString, allSlackUsers, sendDm
from chalicelib.upstash import setEvent, getEvent, getAllKeys, removeEvent

app = Chalice(app_name='birthday-slackbot')
NOTIFY_TIME_LIMIT = int(os.getenv("NOTIFY_TIME_LIMIT"))

# Don't forget to add hashing of the requests...

@app.route('/', methods=["GET"])
def something():
    return {
        "Hello": "World"
        }


@app.route('/', methods=["POST"], content_types=["application/x-www-form-urlencoded"])
def index():
    r = responseToDict(app.current_request.raw_body)

    # command parameters will be splitted via commas (",")
    commandArray = r['text'].split(",")
    command = commandArray[0]

    commandArray.pop(0)

    if command == "set":
        setEvent(commandArray)

    elif command == "get":
        # call with name of the event
        resultDict = getEvent(commandArray[0])
        return {
        'response_type': "ephemeral",
        'text': "Event Details:\n\n Date: {}\nAdditional Info:\n{}".format(resultDict[0], resultDict[1])
        }

    elif command == "get-all":

        allKeys = getAllKeys()
        stringResult = "\n"
        for key in allKeys:
            stringResult += "- " + key + "\n"

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



    return {
        # Ephemeral since it is a suprise!
        'response_type': "ephemeral",
        'text': "splitted: {}".format(commandArray)
        # 'text': "splitted: {}, {}".format(commandArray, res)
        # 'text': """Command: {}, parameters: {}.""".format(r['command'], resultPostChannel['message']['text'])
        }


# Run at 10:00 am (UTC) every day.
@app.schedule(Cron(15, 1, '*', '*', '?', '*'))
def periodicCheck(event):
    allKeys = getAllKeys()
    for key in allKeys:
        handleEvent(key)


def handleEvent(eventName):
    # if first element is @, then it is a birthday, exclude owner.
    birthdayEvent = eventName[0] == '@'
    print("birthdayEvent: {}".format(birthdayEvent))

    eventDict = getEvent(eventName)
    remainingDays = diffWithTodayFromString(eventDict[0]).days

    if birthdayEvent:
        birthdayHandler(eventName, remainingDays)
    else:
        customEventHandler(eventName, remainingDays)


def birthdayHandler(birthdayPerson, remainingDays):
    print("This is birthday of {}!".format(birthdayPerson))

    if remainingDays == 0:
        res1 = postToChannel('general', "Happy birthday <{}>!".format(birthdayPerson))
        print(res1)
    if remainingDays <= NOTIFY_TIME_LIMIT:
        # Send personal message to everyone except for <birthdayPerson>
        dmEveryoneExcept("{} day(s) until {}'s birthday!".format(remainingDays, birthdayPerson), birthdayPerson[1:])


def customEventHandler(eventName, remainingDays):
    print("This is custom event, {}!".format(eventName))
    print("Diff between today and then: {} day(s)!".format(remainingDays))

    if remainingDays == 0:
        postToChannel('general', "{} is here!".format(eventName))
    elif remainingDays <= NOTIFY_TIME_LIMIT:
        postToChannel('general', "{} day(s) until {}!".format(remainingDays, eventName))


def dmEveryoneExcept(message, birthdayPerson):
    usersAndIds = allSlackUsers()
    print(usersAndIds)
    for user in usersAndIds:
        if user[0] != birthdayPerson:
            sendDm(user[1], message)
        