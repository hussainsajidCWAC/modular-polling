import requests

import string
import secrets

import json

class integrations:
    def __init__(self, environment):
        self.environment = environment
        #bunch of things shared between login and runlookup method
        self.host = None
        self.achieveID = None
        self.sessions = None
        self.cookies = None

    def login(self):
       	# Log into portal via front door to obtain session cookies.
        if self.environment == 'live':
            self.host = "https://qwest-forms.achieveservice.com"
        else:
            self.host = "https://qwest-test-forms.achieveservice.com"
        
        uri = self.host + "/"
        url = self.host + "/authapi/auth?auth_session=978f4923d72a14ee5271d90817a32630&provider=ssauth&uri=/RenderAchieveForms"
        payload = {'username': ''}
        response = requests.post(url, data=payload)
        
        # Cache the cookies.
        self.cookies = response.cookies
        
        # Obtain an auth-session ID.
        url = self.host + "/authapi/isauthenticated?uri="+ uri + "&hostname=" + self.host + "&withCredentials=true"
        response = requests.get(url, cookies=self.cookies)
        self.sessions = response.json()["auth-session"]
        
        # Generate a unique AchieveForms ID.
        alphabet = string.ascii_letters + string.digits
        self.achieveID = ''.join(secrets.choice(alphabet) for i in range(14))
    
    def runLookup(self, integrationID, formValues = {}):
        #url for running the lookup
        url = self.host + "/apibroker/runLookup?id=" + integrationID + "&repeat_against=&noRetry=false&getOnlyTokens=undefined&log_id=&app_name=AchieveForms&_="+ self.achieveID + "&sid=" + self.sessions

        payload = {
            'formValues': formValues,
            'created': "",
            'env_tokens': {},
            'formName': "",
            'formUri': "",
            'processId': "",
            'processName': "",
            'reference': "AJAX",
            'tokens': {'port': ""},
            'usePHPIntegrations': True 
        }
        
        response = requests.post(url, json=payload, cookies=self.cookies)

        jsonResponse = json.loads(response.text)['integration']['transformed']

        results = {
             'hasRan': True,
             'success': None,
             'data': jsonResponse
        }

        if 'xml_data' not in jsonResponse:
            #integration has failed
            results['success'] = False
        elif jsonResponse['error']:
            #integration hasn't returned any data. propbably because it's an email integration
            results['success'] = True
        else:
            #all good
            results['success'] = True
            results['data'] = jsonResponse['rows_data']
        
        return results