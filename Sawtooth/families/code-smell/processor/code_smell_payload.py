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

from sawtooth_sdk.processor.exceptions import InvalidTransaction


class codeSmellPayload(object):
    """
    code smell payload, all transactions within the code smell family
    must have the following attributes:
        type of transaction
        asset id, this will depend on the type of transaction
        data
        state, each type of transaction will have a state`
    """

    def __init__(self, payload):
        try:
            #The payload is csv utf-8 encoded string
            type, id, data, state = payload.decode().split(",")
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        if not type:
            raise InvalidTransaction ('Type of transaction is required')
        if not id:
            raise InvalidTransaction ('Asset id is required')
        if not data:
            raise InvalidTransaction('Data is required')
        if not state:
            raise InvalidTransaction('State is required')
        if type not in ('code_smell', 'proposal', 'vote', 'list'):
            raise InvalidTransaction('Invalid action: {}'.format(action))

        self._type = type
        self._id = id
        self._data = data
        self._state = state

    @staticmethod
    def from_bytes(payload):
        return codeSmellPayload(payload=payload)

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @property
    def state(self):
        return self._state
