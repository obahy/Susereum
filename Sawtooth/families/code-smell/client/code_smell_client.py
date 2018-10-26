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
        #pull all transactions of code smell family
        result = self._send_request("transactions")
        #print (result)

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

    def show(self, address):
        """
        list a specific transaction, based on its address

        Args:
            address (str), transaction's address
        """
        result = self._send_request("transactions/{}".format(address))

        transactions = {}
        try:
            encoded_entries = yaml.safe_load(result)["data"]
            #print ( base64.b64decode(encoded_entries["payload"]))
            transactions["payload"] = base64.b64decode(encoded_entries["payload"])
            transactions["header_signature"] = encoded_entries["header_signature"]
            return transactions
        except BaseException:
            return None

    def propose(self, code_smells):
        """
        propose new metrics for the code smell families
        the function assumes that all code smells have been updated even if they don't

        Args:
            code_smells (dict), dictionary of code smells and metrics
        """
        #get code smell family address prefix
        code_smell_prefix = self._get_prefix()

        #check for an active proposal, transactions are return in sequential order.
        proposal_result = self._send_request("state?address={}".format(code_smell_prefix))
        encoded_entries = yaml.safe_load(proposal_result)["data"]
        for entry in encoded_entries:
            #look for the first proposal transactiosn
            if base64.b64decode(entry["data"]).decode().split(',')[0] == "proposal":
                last_proposal = base64.b64decode(entry["data"]).decode().split(',')
                break
                #within the transactions look for an active
                #if base64.b64decode(entry["data"]).decode().split(',')[3] == "active":
                    #return "Invalid Operation, another proposal is Active"
                    #print ( base64.b64decode(entry["data"]).decode().split(',')[3] )
        try:
            if last_proposal[3] == "active":
                return "Invalid Operation, another proposal is Active"
        except BaseException:
            pass

        #if no active proposal continue
        ####################REMOVE THIS##########
        # str_dict = str(code_smells)
        # print ("str: {}".format(str_dict))
        # another_dict = yaml.safe_load(str_dict)
        # print (another_dict)
        # print (another_dict["LargeClass"])
        # for key in another_dict.keys():
        #     print (key)
        #encoded = str(code_smells)
        #print (encoded.replace(",", ";"))

        localtime = time.localtime(time.time())
        transac_time = str(localtime.tm_year) + str(localtime.tm_mon) + str(localtime.tm_mday)
        propose_date = str(transac_time)

        response = self._send_codeSmell_txn(
             id=_sha512( str(code_smells).encode('utf-8') )[0:6],
             type='proposal',
             data=str(code_smells).replace(",", ";"),
             state='active',
             date=propose_date)

        return response

    def _update_proposal(self, proposal, state):
        """
        update proposal, update state.

        Args:
            proposal (dict), proposal data
            sate (str), new proposal's state
        """
        localtime = time.localtime(time.time())
        transac_time = str(localtime.tm_year) + str(localtime.tm_mon) + str(localtime.tm_mday)
        propose_date = str(transac_time)

        response = self._send_codeSmell_txn(
             id=proposal[1],
             type='proposal',
             data=proposal[2],
             state=state,
             date=propose_date)

        ## TODO: call health family to re-calculate health


    def _update_config(self, toml_config, proposal):
        """
        update code smell configuration metrics, after the proposal is accepted
        the configuration file needs to be updated.

        Args:
            toml_config (dict), current configuration
            proposal (str), proposal that contains new configuration
        """
        #get proposal payload
        proposal_payload = yaml.safe_load(proposal[2].replace(";", ","))
        tmp_payload = {}

        #print (proposal_payload)
        #print (toml_config)

        """
        start by traversing the proposal,
        get the code smell and the metric
        """
        for proposal_key, proposal_metric in proposal_payload.items():
            tmp_type = ""
            """
            we don't know where on the toml file is the code smell,
            traverse the toml dictionary looking for the same code smell.
            """
            for type in toml_config["code_smells"]:
                """
                once you found the code smell, break the loop and return
                a pseudo location
                """
                if proposal_key in toml_config["code_smells"][type].keys():
                    tmp_type = type
                    break
            #update configuration
            toml_config["code_smells"][tmp_type][proposal_key] = int(proposal_metric)
            #print (toml_config["code_smells"][tmp_type][proposal_key])

        #save new configuration
        conf_file = self._work_path + '/etc/code_smell.toml'
        try:
            with open(conf_file, 'w+') as config:
                toml.dump(toml_config, config)

            ## TODO: call github an send new code smell. 
        except IOError as e:
            raise codeSmellException ("Unable to open configuration file")

    def _check_votes(self, proposal_id, flag=None):
        """
        review the votes of a proposal

        Args:
            proposal_id (str), proposal id
        """
        result = self._send_request("transactions/{}".format(proposal_id))
        encoded_result = yaml.safe_load(result)["data"]
        proposal = base64.b64decode(encoded_result["payload"]).decode().split(',')
        proposal_id = proposal[1]
        transactions = self.list(type='vote')
        total_votes = 0
        for vote in transactions:
            #for all votes of proposal
            if transactions[vote].decode().split(',')[2] == proposal_id:
                #get vote and count
                total_votes += int(transactions[vote].decode().split(',')[3])

        #get treshold
        """identify code_smell family configuration file"""
        conf_file = self._work_path + '/etc/code_smell.toml'

        if flag is not None:
            if os.path.isfile(conf_file):
                try:
                    with open(conf_file) as config:
                        raw_config = config.read()
                        config.close()
                except IOError as e:
                    raise codeSmellException ("Unable to load code smell family configuration file")

                """load toml config into a dict"""
                parsed_toml_config = toml.loads(raw_config)

                """get treshold"""
                code_smells_config = parsed_toml_config['vote_setting']

                vote_treshold = int(code_smells_config['approval_treshold'])

                if (total_votes >= vote_treshold):
                    self._update_config(parsed_toml_config, proposal)
                    ## TODO: add logic to handle window period check.
                    self._update_proposal(proposal, "accepted")
        else:
            return "Total votes: " + str(total_votes)

    def vote(self, proposal_id, vote):
        """
        vote to accept or reject a proposal

        Args:
            proposal_id (str), id of proposal
            vote (int), value of vote 1=accept, 0=reject
        """

        #verify active proposal
        result = self._send_request("transactions/{}".format(proposal_id))
        encoded_result = yaml.safe_load(result)["data"]
        proposal = base64.b64decode(encoded_result["payload"]).decode().split(',')
        if proposal[3] != 'active':
            return ("Proposal is not active")

        #active proposal, record vote
        response = self._send_codeSmell_txn(
             id=str(random.randrange(1,99999)),
             type='vote',
             data=proposal[1],
             state=str(vote))

        if response is not None:
            self._check_votes(proposal_id,1)

        return response

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
                            date=None,
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
        if type == 'proposal':
            payload = ",".join([type, id, data, state, str(date)]).encode()
        else:
            payload = ",".join([type, id, data, state]).encode()

        pprint("payload: {}".format(payload))######################################## pprint

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
