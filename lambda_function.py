from lookup import integrations
import time
import datetime

def lambda_handler(event, context):
    start = time.time()

    #check if the today is within a blackout_day
    def skip_job(blackout_days):
        current_day = datetime.datetime.today().weekday()

        if blackout_days and current_day in blackout_days:
            return True 

        return False

    #call the given integration and pass the given row as the payload
    def callIntegration(integrationID, row, retry_count = 0):
        payload = {
            'Section 1': {}
        }

        #translate the row into payload
        if (row is not None):
            for token in row:
                payload['Section 1'][token] = {
                    'name': token,
                    'value': row[token]
                }
        
        response = integration.runLookup(integrationID, payload)

        if response['success'] == False and retry_count < 5:
            retry_count += 1

            # exponential backoff
            time.sleep(pow(2, retry_count))

            callIntegration(integrationID, row, retry_count)

        return response['data']

    #for each given row, call the given integration
    def recursiveIntegrationCall(index = 0, rows = {'0': None}):

        def checkConditions(conditions, integrationID, row):
            if conditions is not None:
                if integrationID in conditions:
                    for token in row:
                        if token == conditions[integrationID]['token']:
                            if conditions[integrationID]['value'] != row[token]:
                                return False
            return True

        for i in rows:
            for integrationID in integrationIDs[index]:
                #check if the integration needs running
                valid = checkConditions(conditions, integrationID, rows[i])

                if not valid:
                    continue
                
                newRows = callIntegration(integrationID, rows[i])

                if newRows is None:
                    continue

                if (len(integrationIDs) > index + 1) and len(newRows) > 0:
                    newIndex = index + 1

                    recursiveIntegrationCall(newIndex, newRows)
                    #try:
                    #    recursiveIntegrationCall(newIndex, newRows)
                    #except:
                    #    continue

    environment = 'test'
    
    #basic validations
    if "queryStringParameters" not in event:        
        return 'Invalid parameters'
        
    environment = event['queryStringParameters']['environment']
    integrationIDs = event['queryStringParameters']['integrationIDs']

    conditions = None
    if 'conditions' in event['queryStringParameters']:
        conditions = event['queryStringParameters']['conditions']

    blackout_days = None
    if 'blackout_days' in event['queryStringParameters']:
        blackout_days = event['queryStringParameters']['blackout_days']

    if skip_job(blackout_days):
        return {
            "result": "Skipping the job due to blackout day.",
        }
    
    #integrations initialisation
    integration = integrations(environment)
    integration.login()

    #start
    recursiveIntegrationCall()

    time_lapsed = time.time() - start

    return {
        "result": "All good",
        "time_lapsed": round(time_lapsed, 2)
    }