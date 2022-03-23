from urllib import request
from urllib.parse import parse_qsl
import json
import os

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
 

def channelNameToId(channelName) :
    resultDict = sendPostRequest("https://slack.com/api/conversations.list", SLACK_BOT_TOKEN)
    for channel in resultDict['channels']:
        if (channel['name'] == channelName):
            return channel['id']
    return None

def postToChannel(channel, messageText):
    channelId = channelNameToId(channel)

    # make sure to use double quotes.
    # single quotes creates a dictionary...
    data = {
        "channel": channelId,
        "text": messageText
    }
    data = json.dumps(data)
    data = str(data)
    data = data.encode('utf-8')
    resultDict = sendPostRequest("https://slack.com/api/chat.postMessage", SLACK_BOT_TOKEN, data)
    return resultDict

def sendPostRequest(requestURL, bearerToken, data={}):
    req = request.Request(requestURL, method="POST", data=data)
    req.add_header("Authorization", "Bearer {}".format(bearerToken))
    req.add_header("Content-Type", "application/json; charset=utf-8")
    
    r = request.urlopen(req)
    resultDict = json.loads(r.read().decode()) 
    return resultDict

def responseToDict(res):
    return dict(parse_qsl(res.decode()))

def parseString(string):
    return string.split()

# May not be necessary for the current implementation...
def concatStringFromList(stringList, startIndex):
    string = ""
    for i in range(startIndex, len(stringList)):
        string += (stringList[i] + " ")
    return string