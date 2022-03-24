from urllib import request
from urllib.parse import parse_qsl
import json
import os
from datetime import date


SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def allSlackUsers():
    resultDict = sendPostRequest("https://slack.com/api/users.list", SLACK_BOT_TOKEN)
    members = resultDict['members']
    
    userMembers = []
    for member in members:
        if not member['deleted'] and not member['is_bot']:
            userMembers.append([member['name'], member['id']])
            print(member)
            print(member['name'], member['id'])
            print()
    return userMembers

def channelNameToId(channelName) :
    resultDict = sendPostRequest("https://slack.com/api/conversations.list", SLACK_BOT_TOKEN)
    for channel in resultDict['channels']:
        if (channel['name'] == channelName):
            return channel['id']
    return None

def postToSlack(channelId, messageText):
    data = {
        "channel": channelId,
        "text": messageText
    }
    data = json.dumps(data)
    data = str(data)
    data = data.encode('utf-8')
    resultDict = sendPostRequest("https://slack.com/api/chat.postMessage", SLACK_BOT_TOKEN, data)
    return resultDict

def postToChannel(channel, messageText):
    channelId = channelNameToId(channel)
    return postToSlack(channelId, messageText)

def sendDm(channelId, messageText):
    return postToSlack(channelId, messageText)


def sendPostRequest(requestURL, bearerToken, data={}):
    req = request.Request(requestURL, method="POST", data=data)
    req.add_header("Authorization", "Bearer {}".format(bearerToken))
    req.add_header("Content-Type", "application/json; charset=utf-8")
    
    r = request.urlopen(req)
    resultDict = json.loads(r.read().decode()) 
    return resultDict


def responseToDict(res):
    return dict(parse_qsl(res.decode()))

# May not be necessary for the current implementation...
def concatStringFromList(stringList, startIndex):
    string = ""
    for i in range(startIndex, len(stringList)):
        string += (stringList[i] + " ")
    return string


# Dates are given as: MM-DD
def diffWithTodayFromString(dateString):
    now = date.today()
    currentYear = now.year

    dateTokens = dateString.split("-")
    month = int(dateTokens[0])
    day = int(dateTokens[1])

    if now > date(currentYear, month, day):
        return date((currentYear + 1), month, day) - now
    return date(currentYear, month, day) - now
    