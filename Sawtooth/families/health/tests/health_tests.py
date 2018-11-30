import unittest
import os
import sys
import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from client.helth_client import HealthClient #pylint: disable=import-error
from client.health_exceptions import HealthException #pylint: disable=import-error

class SimpleTest(unittest.TestCase):
    def setUp(self):
        #get default values
        DISTRIBUTION_NAME = 'suserum-health'
        HOME = os.getenv('SAWTOOTH_HOME')
        DEFAULT_URL = 'http://127.0.0.1:8008'

        #get user key
        username = getpass.getuser()
        home = os.path.expanduser("~")
        key_dir = os.path.join(home, ".sawtooth", "keys")
        keyfile = '{}/{}.priv'.format(key_dir, username)

        self.client = HealthClient(base_url=DEFAULT_URL, keyfile=keyfile, work_path=HOME)

        #get test txn_id
        self.txn = self.client.list()
        for entry in self.txn.keys():
            self.txn_id = entry
            break


    def test_commit(self):
        response = self.client.commit(commit_url="github.com", github_id="1234", commit_date="2018-11-26-18-53-12", client_key="tcp://127.0.0.1:1002")
        self.assertNotEqual(response, None)

    def test_code_analysis(self):
        response = self.client.code_analysis(github_url="github.com", github_user="123", commit_date="2018-11-26-18-53-12", client_key="tcp://127.0.0.1:1002")
        self.assertNotEqual(response, None)

    def test_list(self):
        response = self.client.list()
        self.assertNotEqual(response, None)

    def test_list_incorrect_type(self):
        response = self.client.list("noType")
        self.assertEqual(len(response), 0)

    def test_bad_code_analysis(self):
        self.assertRaises(HealthException, self.client.code_analysis, "2331", "github.com", "201826")

if __name__ == '__main__':
    unittest.main()
