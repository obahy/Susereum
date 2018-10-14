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

import os
import toml
import time
import yaml
import random
import base64
import hashlib
import requests

from pprint import pprint
from base64 import b64encode
from sawtooth_signing import ParseError
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

from code_smell_exceptions import codeSmellException

def _sha512(data):
    """
    return hash of data
    Args:
        data (object), object to get hash
    """
    return hashlib.sha512(data).hexdigest()

class codeSmellClient:
    """
    construct and send code smell transaction.
    """
    def __init__(self, base_url, work_path, keyfile=None):
        self._base_url = base_url
        self._work_path = work_path

        if keyfile is None:
            self._signer = None
            return

        try:
            with open(keyfile) as fd:
                private_key_str = fd.read().strip()
        except OSError as err:
            raise codeSmellException('Failed to read private key {}: {}'.format(keyfile, str(err)))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as e:
            raise codeSmellException('Unable to load private key: {}'.format(str(e)))

        self._signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)

    def default(self, wait=None):
        """
        load a defautl code smell configuration
        """

        """identify code_smell family configuration file"""
        conf_file = self._work_path + '/etc/code_smell.toml'
        response = ""

        if os.path.isfile(conf_file):
            try:
                with open(conf_file) as config:
                    raw_config = config.read()
            except IOError as e:
                raise codeSmellException ("Unable to load code smell family configuration file")

            """load toml config into a dict"""
            parsed_toml_config = toml.loads(raw_config)

            """get default code smells"""
            code_smells_config = parsed_toml_config['code_smells']

            """traverse dict and process each code smell
                nested for loop to procces level two dict."""
            for code_smells in code_smells_config.values():
                for name, metric in code_smells.items():
                    """send trasaction"""
                    #print("{},{}".format(name,metric))
                    response = self._send_codeSmell_txn(
                        type='code_smell',
                        id=name,
                        data=str(metric),
                        state='create',
                        wait=wait)
        else:
            raise codeSmellException("Configuration File {} does not exists".format(conf_file))

        return response

    def list(self,type=None):
        """
        list all transactions.

        Args:
            type (str), asset that we want to list (code smells, proposals, votes)
        """
        #get code smell family address prefix
        code_smell_prefix = self._get_prefix()

        #pull all transactions of code smell family
        result = self._send_request("transactions")

        transactions = {}
        try:
            encoded_entries = yaml.safe_load(result)["data"]
            if type is None:
                for entry in encoded_entries:
                    transactions[ entry["header_signature"] ] = base64.b64decode(entry["payload"])

            else:
                for entry in encoded_entries:
                    transaction_type = base64.b64decode(entry["payload"]).decode().split(',')[0]
                    if transaction_type == type:
                        transactions[ entry["header_signature"] ] = base64.b64decode(entry["payload"])

            return transactions
        except BaseException:
            return None

    def create(self, name, value, action, wait=None, auth_user=None, auth_password=None):
        print ("on client", name, value, action)
        return self._send_codeSmell_txn(
            name,
            value,
            action,
            wait=wait,
            auth_user=auth_user,
            auth_password=auth_password)

    def _get_status(self, batch_id, wait, auth_user=None, auth_password=None):
        try:
            result = self._send_request(
                'batch_status?id={}&wait={}'.format(batch_id, wait),
                auth_user=auth_user,
                auth_password=auth_password)
            return yaml.safe_load(result)['data'][0]['status']
        except BaseException as err:
            raise codeSmellException(err)

    def _get_prefix(self):
        """
        get code smell family address prefix
        """
        return _sha512('code-smell'.encode('utf-8'))[0:6]

    def _get_address(self, id):
        """
        get transaction address

        Args:
            id (str): trasaction id
        """
        codeSmell_prefix = self._get_prefix()
        codeSmell_address = _sha512(id.encode('utf-8'))[0:64]
        return codeSmell_prefix + codeSmell_address

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
                raise codeSmellException("No such transaction")
            elif not result.ok:
                raise codeSmellException("Error {}:{}".format(result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise codeSmellException ('Failed to connect to {}:{}'.format(url, str(err)))

        except BaseException as err:
            raise codeSmellException(err)

        return result.text

    def _send_codeSmell_txn(self,
                            type=None,
                            id=None,
                            data=None,
                            state=None,
                            wait=None):
        """
        serialize payload and create header transaction

        Args:
            type (str):    type of transaction
            id (str):      asset id, will depend on type of transaction
            data (object): transaction data
            state (str):   all transactions must have a state
            wait (int):    delay to process transactions
        """
        #serialization is just a delimited utf-8 encoded strings
        payload = ",".join([type, id, data, state]).encode()

        pprint(payload)

        #construct the address
        address = self._get_address(id)


        #construct header`
        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name="code-smell",
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
        transaction = Transaction (
            header=header,
            payload=payload,
            header_signature=signature
        )

        """create batch list, suserum policy: one transaction per batch"""
        batch_list = self._create_batch_list([transaction])
        batch_id = batch_list.batches[0].header_signature

        ## TODO: enable wait logic and test on further releases
        if wait and wait > 0:
            wait_time = 0
            start_time = time.time()
            response = self._send_request(
                "batches", batch_list.SerializeToString(),
                'application/octet-stream',
                auth_user=auth_user,
                auth_password=auth_password)
            while wait_time < wait:
                status = self._get_status(
                    batch_id,
                    wait - int(wait_time),
                    auth_user=auth_user,
                    auth_password=auth_password)

                if status != 'PENDING':
                    return response

            return response

        return self._send_request(
            "batches" ,
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
