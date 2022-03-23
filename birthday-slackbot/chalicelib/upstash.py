from chalicelib.utils import sendPostRequest
import os

UPSTASH_REST_URL = os.getenv("UPSTASH_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_TOKEN")

def postToUpstash(parameters):
    print(parameters)
    requestURL = UPSTASH_REST_URL
    for parameter in parameters:
        requestURL += ("/" + parameter)
    
    resultDict = sendPostRequest(requestURL, UPSTASH_TOKEN)
    return resultDict['result']

def setEvent(parameterArray):
    postQueryParameters = ['RPUSH']

    for parameter in parameterArray:
        parameter = parameter.split()
        for subparameter in parameter:
            postQueryParameters.append(subparameter)

    resultDict = postToUpstash(postQueryParameters)

    print("setEvent result: {}".format(resultDict))
    return resultDict

def getEvent(parameterArray):
    postQueryParameters = ['LRANGE', parameterArray[0], '0', str(2**32 - 1)]
    resultDict = postToUpstash(postQueryParameters)

    print("getEvent result: {}".format(resultDict))

    print(resultDict)
    date = resultDict[0]
    del resultDict[0]
    string = "Date: {}\n Additional info:\n".format(date)

    for element in resultDict:
        string += " " + element

    return string

def getAllEvents():
    # gets all the keys from database
    allKeys = postToUpstash(['KEYS', '*'])

    print(allKeys)
    string = "\n"
    for key in allKeys:
        string += "- " + key + "\n"
    return string

def removeEvent(parameterArray):
    postQueryParameters = ['DEL', parameterArray[0]]

    resultDict = postToUpstash(postQueryParameters)
    print("getEvent result: {}".format(resultDict))

def fetchFromUpstash():
    pass

# def setEvent(commandArray):
    