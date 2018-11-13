# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
"""
Health Family Processor

This processor handles all transaction related to the commit of new code,
whenever users made a commit to github this class will trigger logic to process
the commit and calculate project's health.

Raises:
    health exceptions: health family exceptions to display misuse of functions
"""
import os
import sys
import time
import random
import base64
import hashlib
import yaml
import requests
import subprocess

from pprint import pprint
from base64 import b64encode
from sawtooth_signing import ParseError #pylint: disable=import-error
from sawtooth_signing import CryptoFactory #pylint: disable=import-error
from sawtooth_signing import create_context #pylint: disable=import-error
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey #pylint: disable=import-error

from sawtooth_sdk.protobuf.batch_pb2 import Batch #pylint: disable=import-error
from sawtooth_sdk.protobuf.batch_pb2 import BatchList #pylint: disable=import-error
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader #pylint: disable=import-error
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction #pylint: disable=import-error
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader #pylint: disable=import-error

from client.health_exceptions import HealthException

def _sha512(data):
    """
    return hash of data
    Args:
        data (object), object to get hash
    """
    return hashlib.sha512(data).hexdigest()

class HealthClient:
    """
    construct and send health transaction.
    """
    def __init__(self, base_url, work_path, keyfile=None):
        self._base_url = base_url
        self._work_path = work_path

        if keyfile is None:
            self._signer = None
            return

        try:
            with open(keyfile) as file_ptr:
                private_key_str = file_ptr.read().strip()
        except OSError as err:
            raise HealthException('Failed to read private key {}: {}'.format(keyfile, str(err)))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as parser_error:
            raise HealthException('Unable to load private key: {}'.format(str(parser_error)))

        self._signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)

    def code_analysis(self, github_url, github_user):
        """
        send github url to code analysis to generate new health

        Args:
            github_url (str): commit url
            github_user (str): github user id
        """
        ## TODO: talk to code analysis, and then publish the actual result
        localtime = time.localtime(time.time())
        txn_time = str(localtime.tm_year) + str(localtime.tm_mon) + str(localtime.tm_mday)
        txn_date = str(txn_time)
        work_path = '\\'.join(sys.argv[0].split('\\')[0:-3])
        sawtooth_home = work_path + "/results"

        #get repo path
        conf_file = work_path + '/etc/.repo'
        try:
            with open(conf_file, 'r') as path:
                repo_path = path.read()
            path.close()
        except IOError as error:
            raise HealthException("Unable to open configuration file {}".format(error))

        repo_path = repo_path + '/Code\ Analysis/SourceMeter_Interface/src/sourceMeterWrapper.py'
        save_path = subprocess.check_output(['python',repo_path, github_url, sawtooth_home]).decode('utf-8')
        save_path = save_path[save_path.rfind('OK\n')+4:-4]#check if "OK\n" is in project name or read from file

        response = self._send_health_txn(
            txn_type='health',
            txn_id=github_user,
            data=save_path,
            state='processed',
            txn_date=txn_date)
        return response
        ## TODO: add health to chain
        ## TODO: call suse family to process suse.

    def commit(self, commit_url, github_id):
        """
        Send commit url to code analysis
        """
        response = self._send_health_txn(
            txn_type='commit',
            txn_id=github_id,
            data=commit_url,
            state='new',
            url=self._base_url)

        return response

    def list(self, txn_type=None, limit=None ):
        """
        list all transactions.
        """
        #pull all transactions of health family
        ## TODO: modify logic to pull transactions per family
        if limit is None:
            result = self._send_request("transactions")
        else:
            result = self._send_request("transactions?limit={}".format(limit))
        #
        transactions = {}
        try:
            encoded_entries = yaml.safe_load(result)["data"]
            if txn_type is None:
                for entry in encoded_entries:
                    transactions[entry["header_signature"]] = base64.b64decode(entry["payload"])

            else:
                for entry in encoded_entries:
                    transaction_type = base64.b64decode(entry["payload"]).decode().split(',')[0]
                    if transaction_type == txn_type:
                        transactions[entry["header_signature"]] = base64.b64decode(entry["payload"])

            return transactions
        except BaseException:
            return None


    def _get_prefix(self):
        """
        get health family address prefix
        """
        return _sha512('health'.encode('utf-8'))[0:6]

    def _get_address(self, txn_id):
        """
        get transaction address

        Args:
            id (str): trasaction id
        """
        health_prefix = self._get_prefix()
        health_address = _sha512(txn_id.encode('utf-8'))[0:64]
        return health_prefix + health_address

    def _send_request(self,
                      suffix,
                      data=None,
                      content_type=None,
                      auth_user=None,
                      auth_password=None):
        """
        send request to code smell processor`
        """
        if self._base_url.startswith("http://"):
            url = "{}/{}".format(self._base_url, suffix)
        else:
            url = "http://{}/{}".format(self._base_url, suffix)

        headers = {}
        if auth_user is not None:
            auth_string = "{}:{}".format(auth_user, auth_password)
            b64_string = b64encode(auth_string.encode()).decode()
            auth_header = 'Basic {}'.format(b64_string)
            headers['authorization'] = auth_header

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise HealthException("No such transaction")
            elif not result.ok:
                raise HealthException("Error {}:{}".format(result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise HealthException('Failed to connect to {}:{}'.format(url, str(err)))

        except BaseException as err:
            raise HealthException(err)

        return result.text

    def _send_health_txn(self,
                         txn_type=None,
                         txn_id=None,
                         data=None,
                         state=None,
                         url=None,
                         txn_date=None):
        """
        serialize payload and create header transaction

        Args:
            type (str):    type of transaction
            id (str):      asset id, will depend on type of transaction
            data (object): transaction data
            state (str):   all transactions must have a state
        """
        #serialization is just a delimited utf-8 encoded strings
        if txn_type == 'commit':
            payload = ",".join([txn_type, txn_id, data, state, url]).encode()
        elif txn_type == 'health':
            payload = ",".join([txn_type, txn_id, data, state, str(txn_date)]).encode()

        pprint("payload: {}".format(payload))######################################## pprint

        #construct the address
        address = self._get_address(txn_id)

        #construct header
        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name="health",
            family_version="0.1",
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._signer.get_public_key().as_hex(),
            nonce=hex(random.randint(0, 2**64))
        ).SerializeToString()

        signature = self._signer.sign(header)

        #create transaction
        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        #create batch list, suserum policy: one transaction per batch
        batch_list = self._create_batch_list([transaction])

        return self._send_request(
            "batches",
            batch_list.SerializeToString(),
            'application/octet-stream')

    def _create_batch_list(self, transactions):
        """
        Create the list of batches that the client will send to the REST API

        Args:
            transactions (transaction): transaction(s) included in the batch

        Returns:
            BatchList: a list of batches to send to the REST API
        """
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)

        return BatchList(batches=[batch])
