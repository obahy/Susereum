# Copyright 2018 Intel Corporation
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
# -----------------------------------------------------------------------------
"""
sends transaction state to the chain.
"""
import hashlib

from sawtooth_sdk.processor.exceptions import InternalError #pylint: disable=import-error


CODESMELL_NAMESPACE = hashlib.sha512('code-smell'.encode('utf-8')).hexdigest()[0:6]

def _make_codeSmell_address(transaction_id):
    """
    creates and returns a transaction address based on the transaction id and
    the family namespace

    Returns:
        str: transaction address
    """

    return CODESMELL_NAMESPACE + hashlib.sha512(transaction_id.encode('utf-8')).hexdigest()[:64]

class CodeSmellTransaction:
    """
    define an object of the code smell transaction class

    Args:
        variable (type):  transaction payload
    """

    def __init__(self, trac_type, trac_id, data, state, date=None):
        """
        Constructor, set up transaction attributes

        Args:
            type (str):    transaction type (code smell, proposal, vote)
            id (str):      trasanction id
            data (object): transaction data
            state (str):   transaction status
            owner (str):   user who send the trasanction
        """
        self.trac_type = trac_type
        self.trac_id = trac_id
        self.data = data
        self.state = state
        self.date = date

class CodeSmellState:
    """
    code state class, serialize and send transaction to the chain.
    """

    TIMEOUT = 3

    def __init__(self, context):
        """Constructor

        Ars:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from the transaction processor
        """

        self._context = context
        self._address_cache = {}

    def set_transaction(self, transaction_id, transaction):
        """
        Save transaction state, the transaction state will be send to
        validator.

        Args:
            codeSmell_name (str): The name
            codesmell (codeSmell): The information specifying the current specs.
        """
        transactions = {} #transactions dictionary
        transactions[transaction.trac_type] = transaction

        self._store_codeSmell(transaction_id, transactions=transactions)

    def _store_codeSmell(self, transaction_id, transactions):
        """
        store transaction in the chain. refered as saving the state of the active transaction

        Args:
            transaction_id (str): id to identify the transaction
            transactions (dict):  dictionary of transactions
        """
        address = _make_codeSmell_address(transaction_id)

        state_data = self._serialize(transactions)
        self._address_cache[address] = state_data

        self._context.set_state({address: state_data}, timeout=self.TIMEOUT)

    def _serialize(self, codesmell):
        """Takes a dict of codeSmell objects and serializes them into bytes.

        Args:
            codesmell (dict): codesmell name (str) keys, codesmell values.

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        codesmell_strs = []
        for trac_type, attr in codesmell.items():
            if trac_type == 'proposal':
                codesmell_str = ",".join(
                    [trac_type, attr.trac_id, attr.data, attr.state, attr.date])
            else:
                codesmell_str = ",".join([trac_type, attr.trac_id, attr.data, attr.state])

            codesmell_strs.append(codesmell_str)

        return "|".join(sorted(codesmell_strs)).encode()
