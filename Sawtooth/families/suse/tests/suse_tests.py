import unittest
import os
import sys
import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from client.suse_client import SuseClient #pylint: disable=import-error
from client.suse_exceptions import SuseException #pylint: disable=import-error

class SimpleTest(unittest.TestCase):
    def setUp(self):
        #get default values
        DISTRIBUTION_NAME = 'suserum-suse'
        HOME = os.getenv('SAWTOOTH_HOME')
        DEFAULT_URL = 'http://127.0.0.1:8008'

        #get user key
        username = getpass.getuser()
        home = os.path.expanduser("~")
        key_dir = os.path.join(home, ".sawtooth", "keys")
        keyfile = '{}/{}.priv'.format(key_dir, username)

        self.client = SuseClient(base_url=DEFAULT_URL, keyfile=keyfile, work_path=HOME)

        #get test txn_id
        self.txn = self.client.list()
        for entry in self.txn.keys():
            self.txn_id = entry
            break

    def test_suse(self):
        response = self.client.suse(new_health=99, github_id="1234")
        self.assertNotEqual(response, None)

    def test_list(self):
        response = self.client.list()
        self.assertNotEqual(response, None)

    def test_list_incorrect_type(self):
        response = self.client.list("noType")
        self.assertEqual(len(response), 0)

    def test_bad_suse(self):
        self.assertRaises(SuseException, self.client.code_analysis, "health")

if __name__ == '__main__':
    unittest.main()
