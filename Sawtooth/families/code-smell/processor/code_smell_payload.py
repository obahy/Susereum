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
validate the payload of transactions

Returns:
    payload: transaction payload

Raises:
    InvalidTransaction: identify an invalid transaction
"""


from sawtooth_sdk.processor.exceptions import InvalidTransaction #pylint: disable=import-error


class CodeSmellPayload(object):
    """
    code smell payload, all transactions within the code smell family
    must have the following attributes:
        type of transaction
        asset id, this will depend on the type of transaction
        data
        state, each type of transaction will have a state`
    """

    def __init__(self, payload):
        #The payload is csv utf-8 encoded string
        try:
            """
            identify which type of transaction we got
            """
            if payload.decode().split(",")[0] in ("proposal", "config", "code_smell"):
                trac_type, trac_id, data, state, date = payload.decode().split(",")
            else:
                trac_type, trac_id, data, state = payload.decode().split(",")
                date = None
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        if not trac_type:
            raise InvalidTransaction('Type of transaction is required')
        if not trac_id:
            raise InvalidTransaction('Asset id is required')
        if not data:
            raise InvalidTransaction('Data is required')
        if not state:
            raise InvalidTransaction('State is required')
        if trac_type not in ('code_smell', 'proposal', 'vote', 'config'):
            raise InvalidTransaction('Invalid action: {}'.format(trac_type))

        self._type = trac_type
        self._id = trac_id
        self._data = data
        self._state = state
        self._date = date

    @staticmethod
    def from_bytes(payload):
        """
        return transaction object

        Returns:
            dict: transaction
        """
        return CodeSmellPayload(payload=payload)

    @property
    def trac_type(self):
        """
        return transaction type

        Returns:
            str: type
        """
        return self._type

    @property
    def trac_id(self):
        """
        return transaction id

        Returns:
            str: id
        """
        return self._id

    @property
    def data(self):
        """
        return data

        Returns:
            object: data
        """
        return self._data

    @property
    def state(self):
        """
        return state

        Returns:
            str: state
        """
        return self._state

    @property
    def date(self):
        """
        return date

        Returns:
            str: date
        """
        return self._date
