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

import hashlib
import datetime
from pprint import pprint

from sawtooth_sdk.processor.exceptions import InternalError


CODESMELL_NAMESPACE = hashlib.sha512('code-smell'.encode('utf-8')).hexdigest()[0:6]

def _make_codeSmell_address(id):
    print (id)
    return CODESMELL_NAMESPACE + hashlib.sha512(id.encode('utf-8')).hexdigest()[:64]

class code_smell_transaction:
    def __init__(self, type, id, data, state, owner):
        """
        Constructor, set up transaction attributes

        Args:
            type (str):    transaction type (code smell, proposal, vote)
            id (str):      trasanction id
            data (object): transaction data
            state (str):   transaction status
            owner (str):   user who send the trasanction
        """
        self.type = type
        self.id = id
        self.data = data
        self.state = state
        self.owner = owner

class codeSmellState:
    TIMEOUT = 3

    def __init__(self, context):
        """Constructor

        Ars:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor
        """

        self._context = context
        self._address_cache = {}

    def set_transaction(self, transaction_id, transaction):
        """Store tran in the validator state

        Args:
            codeSmell_name (str): The name
            codesmell (codeSmell): The information specifying the current specs.
        """
        #dictCodeSmells = self._load_codeSmell(codeSmell_name=codeSmell_name)
        transactions = {} #transaction dict
        transactions[transaction.type] = transaction

        self._store_codeSmell(transaction_id, transactions=transactions)

    def _load_codeSmell(self, codeSmell_name):
        address = _make_codeSmell_address(codeSmell_name)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_codeSmell = self._address_cache[address]
                dictCodeSmells = self._deserialize(serialized_codeSmell)
            else:
                dictCodeSmells = {}
        else:
            state_entries = self._context.get_state([address], timeout=self.TIMEOUT)
            if state_entries:
                self._address_cache[address] = state_entries[0].data
                dictCodeSmells = self._deserialize(data=state_entries[0].data)
            else:
                self._address_cache[address] = None
                dictCodeSmells = {}

        return dictCodeSmells

    def _store_codeSmell(self, codeSmell_name, transactions):
        address = _make_codeSmell_address(codeSmell_name)

        state_data = self._serialize(transactions)
        self._address_cache[address] = state_data

        self._context.set_state({address: state_data}, timeout=self.TIMEOUT)

    def _deserialize(self, data):
        """Take bytes stored in state and deserialize them into Python codeSmell Objects

        Args:
            data (bytes): The UTF-8 encoded string stored in state.

        Returns:
            (dict): codesmell name (str) keys, codesmell values.
        """
        dictCodeSmells = {}
        try:
            for codesmell in data.encode().split("|"):
                name, value, action, owner = payload.decode().split(",")

                dictCodeSmells[name] = codeSmell(name, value, action, owner)

        except ValueError:
            raise InternalError("Failed to deserialize codesmell data")

        return dictCodeSmells

    def _serialize(self, codesmell):
        """Takes a dict of codeSmell objects and serializes them into bytes.

        Args:
            codesmell (dict): codesmell name (str) keys, codesmell values.

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        codesmell_strs = []
        for type, g in codesmell.items():
            #print (type, g.id, g.data, g.state, g.owner)
            codesmell_str = ",".join([type, g.id, g.data, g.state, g.owner])
            codesmell_strs.append(codesmell_str)

        return "|".join(sorted(codesmell_strs)).encode()
