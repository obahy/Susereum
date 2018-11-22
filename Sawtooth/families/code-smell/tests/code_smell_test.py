import unittest
import os
import sys
import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from client.code_smell_client import CodeSmellClient #pylint: disable=import-error
from client.code_smell_exceptions import CodeSmellException #pylint: disable=import-error

class SimpleTest(unittest.TestCase):
    def setUp(self):
        #get default values
        DISTRIBUTION_NAME = 'suserum-code_smell'
        HOME = os.getenv('SAWTOOTH_HOME')
        DEFAULT_URL = 'http://127.0.0.1:8008'

        #get user key
        username = getpass.getuser()
        home = os.path.expanduser("~")
        key_dir = os.path.join(home, ".sawtooth", "keys")
        keyfile = '{}/{}.priv'.format(key_dir, username)

        self.client = CodeSmellClient(base_url=DEFAULT_URL, keyfile=keyfile, work_path=HOME)

        #get test txn_id
        self.txn = self.client.list()
        for entry in self.txn.keys():
            self.txn_id = entry
            break


    def test_load_default(self):
        response = self.client.default()
        self.assertNotEqual(response, None)

    def test_default_repo_id(self):
        response = self.client.default(12345)
        self.assertNotEqual(response, None)

    def test_list(self):
        response = self.client.list()
        self.assertNotEqual(response, None)

    def test_list_incorrect_type(self):
        response = self.client.list("noType")
        self.assertEqual(len(response), 0)

    def test_bad_vote(self):
        self.assertRaises(CodeSmellException, self.client.vote, "234", "yes")

    def test_show_txn(self):
        response = self.client.show(self.txn_id)
        self.assertNotEqual(response, None)

    def test_incorrect_proposal_update(self):
        self.assertRaises(CodeSmellException, self.client._update_suse_file, "LargeClass=kx,Smal")

if __name__ == '__main__':
    unittest.main()
