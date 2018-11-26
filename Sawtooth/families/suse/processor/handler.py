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
suse family handler, verifies that transaction's payload
"""
import logging
from pprint import pprint

from sawtooth_sdk.processor.exceptions import InvalidTransaction #pylint: disable=import-error
from sawtooth_sdk.processor.handler import TransactionHandler #pylint: disable=import-error

from processor.suse_state import SuseTransaction
from processor.suse_state import SuseState
from processor.suse_state import SUSE_NAMESPACE
from processor.suse_payload import SusePayload

LOGGER = logging.getLogger(__name__)

class SuseTransactionHandler(TransactionHandler):
    """
    process all types of transactions regarding the suse family
    """
    def __init__(self):
        self.count_access = 0

    @property
    def family_name(self):
        """
        returns family name

        Returns:
            suse: family name
        """
        return 'suse'

    @property
    def family_versions(self):
        """
        returns family version

        Returns:
            family version
        """
        return ['0.1']

    @property
    def namespaces(self):
        """
        returns family namespace

        Returns:
            family namespace
        """
        return [SUSE_NAMESPACE]

    def apply(self, transaction, context): #pylint: disable=R0201
        """
        process transaction

        validate and process the transaction, review payload and decide which
        action is required.

        Args:
            trasaction (transaction): transaction to process

        Returns:
            None

        Raises:
            InvalidTransaction: display message if we receive and invalid transaction
        """
        suse_payload = SusePayload.from_bytes(transaction.payload)
        suse_state = SuseState(context)

        if suse_payload.txn_type == 'suse':
            active_transaction = SuseTransaction(
                txn_type=suse_payload.txn_type,
                txn_id=suse_payload.txn_id,
                data=suse_payload.data,
                state=suse_payload.state,
                txn_date=suse_payload.txn_date)
            suse_state.set_transaction(suse_payload.txn_id, active_transaction)
        else:
            raise InvalidTransaction('Unhandled Type: {}'.format(suse_payload.txn_type))

        _display("transaction {},{} created".
                 format(suse_payload.txn_type, suse_payload.data))

def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        lenght = max(len(line) for line in msg)
    else:
        lenght = len(msg)
        msg = [msg]

    #pylint: disable=logging-not-lazy
    LOGGER.debug("+" + (lenght + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+ " + line.center(lenght) + " +")
    LOGGER.debug("+" + (lenght + 2) * "-" + "+")
