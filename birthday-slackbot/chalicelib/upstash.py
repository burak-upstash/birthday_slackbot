from chalicelib.utils import sendPostRequest
import os

UPSTASH_REST_URL = os.getenv("UPSTASH_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_TOKEN")

def postToUpstash(parameters):
    requestURL = UPSTASH_REST_URL
    for parameter in parameters:
        requestURL += ("/" + parameter)
    
    resultDict = sendPostRequest(requestURL, UPSTASH_TOKEN)
    return resultDict


def fetchFromUpstash():
    pass