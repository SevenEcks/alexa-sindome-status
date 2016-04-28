'''
This application will act as status reporter for Sindome (www.sindome.org).  You can find the sourcecode on GitHub
at https://github.com/SevenEcks/alexa-sindome-status
'''

from __future__ import print_function
import random
import json
import os
import config
import urllib

# --------------- Helper Functions ------------------
def debug(data):
    '''if debugging is enabled this will push debugs to the logs'''
    if config.DEBUG:
        print(data)

def load_session(event):
    config.session = event['session']
    
def save_intent_name(intent_name):
    '''save the intent_name to pass into session attributes'''
    config.session['attributes']['last_intent_name'] = intent_name
    #should update a session var
    
def get_saved_intent_name():
    '''get the saved last_intent_name for use in session attributes'''
    return config.session['attributes']['last_intent_name'] if 'last_intent_name' in config.session['attributes'] else None

def get_session_attributes():
    '''return a json dump of the session_attributes for passing back with the response'''
    return json.loads(json.dumps(config.session['attributes']))

def load_json_from_file(file_name):
    '''load a json file into a data structure we can reference'''
    with open(file_name) as data_file:
        data = json.load(data_file)
    return data

def random_file(directory):
    '''get a random filename from the directory provided'''
    return random.choice(os.listdir(directory))

def get_sindome_status():
    '''get the status of sindome from the status API'''
        #call the sindome status API
    response = urllib.urlopen(config.SINDOME_STATUS_URL)
    sindome_status = json.loads(response.read())
    debug(sindome_status)
    return sindome_status

def detailed_sindome_status():
    '''get a detailed response on the sindome system status'''
    pass

def basic_sindome_status():
    '''parse the json response into variables'''
    sindome_status = get_sindome_status()
    down_names = [dict['name'] for dict in sindome_status['checks'] if dict['status'] != "up"]
    debug(sindome_status['checks'])
    down = len(down_names)
    up = len(sindome_status['checks']) - down
    timestamp = sindome_status['timestamp']
    return {'up' : up, 'down' : down, 'down names' : down_names, 'timestamp' : timestamp}

# --------------- Functions that control the skill's behavior ------------------
def get_help(intent, session):
    '''tell the user a list of valid commands'''
    #load the json data for this intent
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + get_help.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def get_sindome(intent, session):
    '''tell the user about sindome'''
    #load the json data for this intent
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + get_sindome.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def get_status_overview():
    '''If we wanted to initialize the session to have some attributes we could add those here'''
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + get_status_overview.__name__ + config.SPEECH_FORMAT)
    basic_status = basic_sindome_status()
    debug(response_data['response'])
    response_data['response'] = response_data['response'].format(basic_status['up'], basic_status['down'])
    should_end_session = False
    #save_intent_name(intent)
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def handle_stop(intent, session):
    '''User has requested a stop, so we exit'''
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + handle_stop.__name__ + config.SPEECH_FORMAT)
    should_end_session = True
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def invalid_intent_response(intent, session):
    '''Invalid intention due to the user asking for something we are not sure how to process'''
    debug(intent)
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + invalid_intent_response.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def repeat_intent(intent_request, session):
    #confirm we are not going to recall with the same repeatintent over and over
    last_intent_name = get_saved_intent_name()
    debug('LAST INTENT NAME' + last_intent_name)
    debug('UNEDITED INTENT REQUEST')
    debug(intent_request)
    if last_intent_name and last_intent_name != "AMAZON.RepeatIntent":
        #overwrite the intent where needed
        intent_request['intent']['name'] = last_intent_name
        debug("EDITED INTENT REQUEST")
        debug(intent_request)
        #return False
        return on_intent(intent_request, session)
    debug("SKIPPED INTENT EDIT, RETURNING BAD REPEAT")
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + repeat_intent.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent_request['intent'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))
# --------------- Skill Dipatcher Functions ------------------

def on_intent(intent_request, session):
    '''Called when the user specifies an intent for this skill'''
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    debug(intent_name)
    # Dispatch to your skill's intent handlers
    if intent_name == "Sindome":
        return get_sindome(intent, session)
    elif intent_name == "StatusOverview":
        return get_status_overview(intent, session)
    #handle help, repeating, exiting and stopping properly
    elif intent_name == "AMAZON.RepeatIntent":
        #call with full intent request so we can make the full on_intent call again
        return repeat_intent(intent_request, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help(intent, session)
    elif intent_name == "AMAZON.StopIntent" or intent_name == 'AMAZON.CancelIntent':
        return handle_stop(intent, session)
    else:
        return invalid_intent_response(intent, session)

def process_request(event, context):
    '''Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    '''
    debug(event)

    #Prevent someone else from configuring a skill that sends requests to this function.
    if (config.RESTRICT_ACCESS and event['session']['application']['applicationId'] != 
        config.APPLICATION_ID):
        #TODO make this return a response via alexa?
        raise ValueError("Invalid Application ID")
    #save the session data
    load_session(event)
    debug('SESSION')
    debug(config.session)
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    '''Called when the session starts'''
    #attributes does not already exist on a new session
    config.session['attributes'] = {'last_intent_name' : 'None'}

def on_launch(launch_request, session):
    '''Called when the user launches the skill without specifying an intent '''
    return get_status_overview()

def on_session_ended(session_ended_request, session):
    '''Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    '''
    pass

# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    response = {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    debug('RESPONSE')
    debug(response)
    return response