from chalice import Chalice, Cron, Rate
import os
import random
from datetime import date
from chalicelib.utils import responseToDict, postToChannel, diffWithTodayFromString, allSlackUsers, sendDm
from chalicelib.upstash import setHandler, getAllHandler, getEvent, getAllKeys, removeEvent

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
    commandArray = r['text'].split()
    command = commandArray.pop(0)

    if command == "set":
        setHandler(commandArray)

    elif command == "get":
        # call with name of the event
        eventType = commandArray[0]
        eventName = eventType + "-" + commandArray[1]
        resultDict = getEvent(eventName)
        return {
        'response_type': "ephemeral",
        'text': "`{}` Details:\n\n Date: {}\nRemaining: {} days!".format(eventName, resultDict[0], resultDict[1])
        # 'text': "{} Details:\n\n Date: {}\nAdditional Info:\n{}".format(eventName, resultDict[0], resultDict[1])
        }

    elif command == "get-all":

        stringResult = getAllHandler(commandArray)
        return {
        'response_type': "ephemeral",
        'text': "{}".format(stringResult)
        }

    elif command == "remove":
        eventName = "{}-{}".format(commandArray[0], commandArray[1])
        removeEvent(eventName)
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
@app.schedule(Cron(7, 11, '*', '*', '?', '*'))
def periodicCheck(event):
    allKeys = getAllKeys()
    for key in allKeys:
        handleEvent(key)


# This will need to change
def handleEvent(eventName):
    eventSplitted = eventName.split('-')

    eventType = eventSplitted[0]
    # discard @ or ! as a first character
    personName = eventSplitted[1][1:]
    personMention = convertToCorrectMention(personName)

    eventDict = getEvent(eventName)
    remainingDays = eventDict[1]
    totalTime = eventDict[2]


    if eventType == "birthday":
        birthdayHandler(personMention, personName, remainingDays)
    
    elif eventType == "anniversary":
        print("Anniversary handler")
        anniversaryHandler(personMention, personName, remainingDays, "SOME TIME CALCULATOR HERE!")

    elif eventType == "custom":
        eventMessage = "Not specified"
        if len(eventSplitted) == 3:
            eventMessage = eventSplitted[2]
        customHandler(eventMessage, personMention, personName, remainingDays)


def birthdayHandler(personMention, personName, remainingDays):
    if remainingDays == 0:
        sendRandomBirthdayToChannel('general', personMention)
    if remainingDays <= NOTIFY_TIME_LIMIT:
        # Send personal message to everyone except for <birthdayPerson>
        dmEveryoneExcept("{} day(s) until {}'s birthday!".format(remainingDays, personMention), personName)

def anniversaryHandler(personMention, personName, remainingDays, totalTime):
    if remainingDays == 0:
        sendRandomAnniversaryToChannel('general', personMention)
    if remainingDays <= NOTIFY_TIME_LIMIT:
        # Send personal message to everyone except for <birthdayPerson>
        dmEveryoneExcept("{} day(s) until {}'s anniversary! It is their {} year!".format(remainingDays, personMention, totalTime), personName)

def customHandler(eventMessage, personMention, personName, remainingDays):
    if remainingDays == 0:
        postToChannel('general', "`{}` is here {}!".format(eventMessage, personMention))
    elif remainingDays <= NOTIFY_TIME_LIMIT:
        dmEveryoneExcept("{} day(s) until `{}`!".format(remainingDays, eventMessage), personName)
        # postToChannel('general', "{} day(s) until {}!".format(remainingDays, eventName))


def dmEveryoneExcept(message, person):
    print("DM {} except {}".format(message, person))
    usersAndIds = allSlackUsers()
    for user in usersAndIds:
        if user[0] != person:
            sendDm(user[1], message)
        


# res1 = postToChannel('general', "Happy birthday <!channel>!")


def sendRandomBirthdayToChannel(channel, personMention):
    messageList = [
        "#1-Birthday {}".format(personMention),
        "#2-Birthday {}".format(personMention),
        "#3-Birthday {}".format(personMention),
    ]
    message = random.choice(messageList)
    return postToChannel('general', message)

def sendRandomAnniversaryToChannel(channel, personMention, totalTime):
    messageList = [
        "#1-Anniversary {} for {}th year".format(personMention, totalTime),
        "#2-Anniversary {} for {}th year".format(personMention, totalTime),
        "#3-Anniversary {} for {}th year".format(personMention, totalTime),
    ]
    message = random.choice(messageList)
    return postToChannel('general', message)


def convertToCorrectMention(name):
    if name == "channel" or name == "here" or name == "everyone":
        print(name.split("@"))
        return "<!{}>".format(name)
    else:
        return "<@{}>".format(name)



allKeys = getAllKeys()
for key in allKeys:
    handleEvent(key)