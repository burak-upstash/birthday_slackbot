from chalice import Chalice
from urllib.parse import parse_qsl

app = Chalice(app_name='birthday-slackbot')



@app.route('/', methods=["POST"], content_types=["application/x-www-form-urlencoded"])
def index():
    r = dict(parse_qsl(app.current_request.raw_body.decode()))

    return {
        'response_type': "ephemeral",
        'text': """You wrote {}.""".format(r['text'])
        }


def postToUpstash(command, parameters):
    pass



def fetchFromUpstash():
    pass



