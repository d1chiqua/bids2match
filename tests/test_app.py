import sys
import os
import json
import unittest
from unittest.mock import patch

# Add the project root to sys.path so that the app package can be imported.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import app

class TestMaxAcceptedProposals(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def get_payload(self, max_proposals):
        """
        Returns a payload with the given max_accepted_proposals value.
        """
        return {
            "tid": [4427, 4428, 4429, 4430],
            "users": {
                "40763": {
                    "bids": [
                        { "tid": 4430, "priority": 1, "timestamp": "Sun, 15 Nov 2020 17:16:51 EST -05:00" },
                        { "tid": 4427, "priority": 3, "timestamp": "Sun, 15 Nov 2020 17:16:52 EST -05:00" },
                        { "tid": 4428, "priority": 2, "timestamp": "Sun, 15 Nov 2020 17:16:53 EST -05:00" }
                    ],
                    "otid": 4429
                },
                "40764": {
                    "bids": [
                        { "tid": 4429, "priority": 3, "timestamp": "Sun, 15 Nov 2020 17:16:34 EST -05:00" },
                        { "tid": 4430, "priority": 2, "timestamp": "Sun, 15 Nov 2020 17:16:35 EST -05:00" },
                        { "tid": 4428, "priority": 1, "timestamp": "Sun, 15 Nov 2020 17:16:37 EST -05:00" }
                    ],
                    "otid": 4427
                },
                "40765": {
                    "bids": [
                        { "tid": 4427, "priority": 3, "timestamp": "Sun, 15 Nov 2020 17:17:15 EST -05:00" },
                        { "tid": 4430, "priority": 2, "timestamp": "Sun, 15 Nov 2020 17:17:16 EST -05:00" },
                        { "tid": 4429, "priority": 1, "timestamp": "Sun, 15 Nov 2020 17:17:17 EST -05:00" }
                    ],
                    "otid": 4428
                }
            },
            "max_accepted_proposals": max_proposals
        }

    def test_max_accepted_proposals_4(self):
        payload = self.get_payload(4)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with max proposals 4:", data)
        # You can add more assertions here based on your expectations.

    def test_max_accepted_proposals_2(self):
        payload = self.get_payload(2)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with max proposals 2:", data)
        # Additional assertions based on expected outcomes can be added here.

    def test_max_accepted_proposals_1(self):
        payload = self.get_payload(1)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with max proposals 1:", data)
        # You can check that each student receives only one assignment as expected.

    def test_original_max_accepted_proposals_3(self):
        # Original test for max_accepted_proposals = 3
        payload = self.get_payload(3)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with max proposals 3:", data)

class TestVaryingUserCounts(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def generate_payload(self, num_users):
        """
        Generates a payload with constant:
          - max_accepted_proposals = 3
          - topic IDs: [4427, 4428, 4429, 4430]
        and a variable number of users.
        For each user, we alternate between two bid patterns.
        """
        payload = {
            "tid": [4427, 4428, 4429, 4430],
            "users": {},
            "max_accepted_proposals": 3
        }
        for i in range(1, num_users + 1):
            # Create a unique user ID.
            user_id = str(40000 + i)
            # Alternate between two different bid patterns for variety.
            if i % 2 == 0:
                bids = [
                    { "tid": 4430, "priority": 1, "timestamp": "Sun, 15 Nov 2020 17:16:51 EST -05:00" },
                    { "tid": 4427, "priority": 3, "timestamp": "Sun, 15 Nov 2020 17:16:52 EST -05:00" },
                    { "tid": 4428, "priority": 2, "timestamp": "Sun, 15 Nov 2020 17:16:53 EST -05:00" }
                ]
                otid = 4429
            else:
                bids = [
                    { "tid": 4429, "priority": 3, "timestamp": "Sun, 15 Nov 2020 17:16:34 EST -05:00" },
                    { "tid": 4430, "priority": 2, "timestamp": "Sun, 15 Nov 2020 17:16:35 EST -05:00" },
                    { "tid": 4428, "priority": 1, "timestamp": "Sun, 15 Nov 2020 17:16:37 EST -05:00" }
                ]
                otid = 4427
            payload["users"][user_id] = {
                "bids": bids,
                "otid": otid
            }
        return payload

    def validate_response(self, payload, response_data):
        # Verify that the response contains as many entries as there are users.
        self.assertEqual(len(response_data), len(payload["users"]))
        # For each user, check that they received no more than 3 topics,
        # and that each assigned topic is one of the valid topic IDs.
        for user_id, proposals in response_data.items():
            self.assertLessEqual(len(proposals), payload["max_accepted_proposals"])
            for proposal in proposals:
                self.assertIn(proposal, payload["tid"])

    def test_users_count_1(self):
        payload = self.generate_payload(1)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with 1 user:", data)
        self.validate_response(payload, data)

    def test_users_count_2(self):
        payload = self.generate_payload(2)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with 2 users:", data)
        self.validate_response(payload, data)

    def test_users_count_3(self):
        payload = self.generate_payload(3)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with 3 users:", data)
        self.validate_response(payload, data)

    def test_users_count_4(self):
        payload = self.generate_payload(4)
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with 4 users:", data)
        self.validate_response(payload, data)

class TestTopicMatchingWithBidsInput(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_specific_input_with_bids(self):
        payload = {
            "tid": [3969, 3970, 3971, 3972, 3973, 3974, 3975, 3976, 3977],
            "users": {
                "36239": {
                    "bids": [
                        {
                            "tid": 3969,
                            "priority": 2,
                            "timestamp": "Thu, 12 Nov 2020 12:01:06 EST -05:00"
                        },
                        {
                            "tid": 3970,
                            "priority": 1,
                            "timestamp": "Thu, 12 Nov 2020 12:01:07 EST -05:00"
                        }
                    ],
                    "otid": 3977
                },
                "36240": {
                    "bids": [
                        {
                            "tid": 3971,
                            "priority": 2,
                            "timestamp": "Thu, 12 Nov 2020 12:01:08 EST -05:00"
                        },
                        {
                            "tid": 3972,
                            "priority": 1,
                            "timestamp": "Thu, 12 Nov 2020 12:01:03 EST -05:00"
                        }
                    ],
                    "otid": 3976
                },
                "36241": {
                    "bids": [
                        {
                            "tid": 3973,
                            "priority": 1,
                            "timestamp": "Thu, 12 Nov 2020 12:00:22 EST -05:00"
                        },
                        {
                            "tid": 3974,
                            "priority": 2,
                            "timestamp": "Thu, 12 Nov 2020 12:00:25 EST -05:00"
                        }
                    ],
                    "otid": 3975
                },
                "36242": {
                    "bids": [
                        {
                            "tid": 3975,
                            "priority": 2,
                            "timestamp": "Wed, 11 Nov 2020 12:15:43 EST -05:00"
                        },
                        {
                            "tid": 3976,
                            "priority": 1,
                            "timestamp": "Thu, 12 Nov 2020 11:59:40 EST -05:00"
                        }
                    ],
                    "otid": 3974
                },
                "36243": {
                    "bids": [
                        {
                            "tid": 3976,
                            "priority": 2,
                            "timestamp": "Wed, 11 Nov 2020 11:34:50 EST -05:00"
                        },
                        {
                            "tid": 3977,
                            "priority": 1,
                            "timestamp": "Wed, 11 Nov 2020 12:30:16 EST -05:00"
                        }
                    ],
                    "otid": 3972
                }
            },
            "max_accepted_proposals": 3
        }

        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        print("Response with specific input:", data)    

        self.assertEqual(len(data), len(payload["users"]))

class TestExceptionHandling(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_no_json_input(self):
        # Send a POST request without JSON input.
        response = self.client.post('/match_topics', data="Not JSON", content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertEqual(data["error"], "Bad Request")
        self.assertIn("No JSON input provided", data["message"])

    def test_bad_json_input_missing_tid(self):
        # Send JSON payload missing the required 'tid' key.
        payload = {
            "users": {
                "40763": {
                    "bids": [
                        {"tid": 4430, "priority": 1, "timestamp": "Sun, 15 Nov 2020 17:16:51 EST -05:00"}
                    ],
                    "otid": 4429
                }
            },
            "max_accepted_proposals": 3
        }
        response = self.client.post(
            '/match_topics',
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertEqual(data["error"], "Bad Request")
        self.assertIn("Invalid input", data["message"])

    def test_server_error_during_matching(self):
        # Use a valid payload but simulate an exception during the matching process.
        payload = {
            "tid": [4427, 4428, 4429, 4430],
            "users": {
                "40763": {
                    "bids": [
                        {"tid": 4430, "priority": 1, "timestamp": "Sun, 15 Nov 2020 17:16:51 EST -05:00"}
                    ],
                    "otid": 4429
                }
            },
            "max_accepted_proposals": 3
        }
        # Patch TopicsMatcher.get_student_topic_matches to force an exception.
        from app import topics_matcher
        with patch.object(topics_matcher.TopicsMatcher, "get_student_topic_matches", side_effect=Exception("Forced error")):
            response = self.client.post(
                '/match_topics',
                data=json.dumps(payload),
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data.decode())
            self.assertEqual(data["error"], "Server Error")
            self.assertIn("Forced error", data["message"])

if __name__ == '__main__':
    unittest.main()
