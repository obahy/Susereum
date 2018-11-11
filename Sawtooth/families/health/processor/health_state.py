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

HEALTH_NAMESPACE = hashlib.sha512('health'.encode('utf-8')).hexdigest()[0:6]

def _make_health_address(transaction_id):
    """
    creates and returns a transaction address based on the transaction id and
    the family namespace

    Returns:
        str: transaction address
    """
    return HEALTH_NAMESPACE + hashlib.sha512(transaction_id.encode('utf-8')).hexdigest()[:64]

class HealthTransaction:
    """
    define an object of the code smell transaction class

    Args:
        variable (type):  transaction payload
    """

    def __init__(self, txn_type, txn_id, data, state):
        """
        Constructor, set up transaction attributes

        Args:
            type (str):    transaction type (code smell, proposal, vote)
            id (str):      trasanction id
            data (object): transaction data
            state (str):   transaction status
        """
        self.txn_type = txn_type
        self.txn_id = txn_id
        self.data = data
        self.state = state

class HealthState:
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

    def set_transaction(self, txn_id, transaction):
        """
        Save transaction state, the transaction state will be send to
        validator.

        Args:
            codeSmell_name (str): The name
            codesmell (codeSmell): The information specifying the current specs.
        """
        transactions = {} #transactions dictionary
        transactions[transaction.txn_type] = transaction

        self._store_health(txn_id, transactions=transactions)

    def _store_health(self, txn_id, transactions):
        """
        store transaction in the chain. refered as saving the state of the active transaction

        Args:
            transaction_id (str): id to identify the transaction
            transactions (dict):  dictionary of transactions
        """
        address = _make_health_address(txn_id)

        state_data = self._serialize(transactions)
        self._address_cache[address] = state_data

        self._context.set_state({address: state_data}, timeout=self.TIMEOUT)

    def _serialize(self, transactions):
        """Takes a dict of objects and serializes them into bytes.

        Args:
            transactions (dict): dictionary of transactions

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        transaction_strs = []
        for txn_type, attr in transactions.items():
            transaction_str = ",".join([txn_type, attr.txn_id, attr.data, attr.state])

            transaction_strs.append(transaction_str)

        return "|".join(sorted(transaction_strs)).encode()
