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


class HealthPayload(object):
    """
    health payload, all transactions within the health family
    must have the following attributes:
        type of transaction
        asset id, this will depend on the type of transaction
        data
        state, each type of transaction will have a state`
    """

    def __init__(self, payload):
        #The payload is csv utf-8 encoded string
        try:
            if payload.decode().split(",")[0] in ("commit", "health"):
                txn_type, txn_id, data, state, url, txn_date = payload.decode().split(",")
            else:
                txn_type, txn_id, data, state, txn_date = payload.decode().split(",")
                url = None
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        if not txn_type:
            raise InvalidTransaction('Type of transaction is required')
        if not txn_id:
            raise InvalidTransaction('Asset id is required')
        if not data:
            raise InvalidTransaction('Data is required')
        if not state:
            raise InvalidTransaction('State is required')
        if txn_type not in ('commit', 'health'):
            raise InvalidTransaction('Invalid action: {}'.format(txn_type))

        self._txn_type = txn_type
        self._txn_id = txn_id
        self._data = data
        self._state = state
        self._url = url
        self._txn_date = txn_date

    @staticmethod
    def from_bytes(payload):
        """
        return transaction object

        Returns:
            dict: transaction
        """
        return HealthPayload(payload=payload)

    @property
    def txn_type(self):
        """
        return transaction type

        Returns:
            str: type
        """
        return self._txn_type

    @property
    def txn_id(self):
        """
        return transaction id

        Returns:
            str: id
        """
        return self._txn_id

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
    def url(self):
        """
        return URL

        Returns:
            str: url
        """
        return self._url

    @property
    def txn_date(self):
        """
        return  date

        Returns:
            str: date
        """
        return self._txn_date
