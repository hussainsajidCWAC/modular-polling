from lambda_function import lambda_handler
import unittest
import datetime

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_linear(self):
        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['669f586074915'],
                    ['669f58853d1f4'],
                    ['669f58d9c5804']
                ]
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'All good')

    def test_linear_no_data(self):
        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['66b9d1c2ae68d'],
                    ['669f58853d1f4'],
                    ['669f58d9c5804']
                ]
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'All good')

    def test_multiples(self):
        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['669f586074915'],
                    ['669f58853d1f4','66bc649972920'],
                    ['669f58d9c5804']
                ]
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'All good')

    def test_slowwwww(self):
        #should take at least 2 minutes to complete
        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['66bdf7349f2f5'],
                    ['66bdf7b7861a5']
                ]
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'All good')

    def test_value_condition(self):
        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['66bf3eb071d1b'],
                    ["66bf3f127876a","66bf3f08f1d13"]
                ],
                "conditions": {
                    "66bf3f127876a": {
                        "token": "responseCode",
                        "value": "HA1"
                    },
                    "66bf3f08f1d13": {
                        "token": "responseCode",
                        "value": "HA2"
                    },
                }
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'All good')

    def test_day_condition_skip(self):
        current_day = datetime.datetime.today().weekday()

        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['66bf3eb071d1b']
                ],
                "blackout_days": [current_day] # 0: monday, 7: sunday
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'Skipping the job due to blackout day.')

    def test_day_condition_complete(self):
        current_day = datetime.datetime.today().weekday()

        blackout_day = 0

        if current_day == blackout_day:
            blackout_day = 1

        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['66bf3eb071d1b']
                ],
                "blackout_days": [blackout_day] # 0: monday, 7: sunday
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'All good')

    def test_specific(self):
        event = {
            "queryStringParameters": {
                "environment": 'test',
                "integrationIDs": [
                    ['5d52d3e459313'],
                    ['5d52ce9c26d98']
                ]
            }
        }

        outcome = lambda_handler(event, None)

        self.assertEqual(outcome['result'], 'All good')

if __name__ == '__main__':
    unittest.main()