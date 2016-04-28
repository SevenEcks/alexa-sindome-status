'''configuration variables for use throughout the global scope'''
session = None
# --------------- Static Variables ------------------
APPLICATION_ID = 'amzn1.echo-sdk-ams.app.1a291230-7f25-48ed-b8b7-747205d072db'
APPLICATION_NAME = 'The Cyberpunk Dictionary'
APPLICATION_INVOCATION_NAME = 'the cyberpunk dictionary'
APPLICATION_VERSION = '0.1'
APPLICATION_ENDPOINT = 'arn:aws:lambda:us-east-1:099464953977:function:process_request'
SINDOME_STATUS_URL = 'http://status.sindome.org/checks/'
SPEECH_DIRECTORY = 'speech/'
SPEECH_FORMAT = '.json'
#in production this value should be set to True if you want to confirm someone has the right application id
RESTRICT_ACCESS = False
#turn on or off debugging
DEBUG = True