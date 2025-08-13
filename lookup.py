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

        results = {
             'hasRan': True,
             'success': None,
             'data': None
        }

        # check if the response is okay
        if response.status_code != 200:
            results['success'] = False

            return results

        # sometimes the int runs okay but returns an empty response
        if response.text == '':
            results['success'] = False

            return results

        jsonResponse = json.loads(response.text)

        # check if the response contains an error
        if 'error' in jsonResponse:
            results['success'] = False

            return results
        
        if jsonResponse['integration']['type'] == 'email':
            # this is an email integration, so we don't have any data to return
            results['success'] = True
            results['data'] = None

            return results

        try:
            results['data'] = jsonResponse['integration']['transformed']['rows_data']
            results['success'] = True
        except:
            results['success'] = False

        return results