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
health family handler, verifies that transaction's payload
"""
import logging
from pprint import pprint

from sawtooth_sdk.processor.exceptions import InvalidTransaction #pylint: disable=import-error
from sawtooth_sdk.processor.handler import TransactionHandler #pylint: disable=import-error

from processor.health_state import HealthTransaction
from processor.health_state import HealthState
from processor.health_state import HEALTH_NAMESPACE
from processor.health_payload import HealthPayload
from client.health_cli import process_health

LOGGER = logging.getLogger(__name__)

class HealthTransactionHandler(TransactionHandler):
    """
    process all types of transactions regarding the code smell family
    """
    def __init__(self):
        self.count_access = 0

    @property
    def family_name(self):
        """
        returns family name

        Returns:
            code_smell: family name
        """
        return 'health'

    @property
    def family_versions(self):
        """
        returns family version

        Returns:
            family name
        """
        return ['0.1']

    @property
    def namespaces(self):
        """
        returns family namespace

        Returns:
            family namespace
        """
        return [HEALTH_NAMESPACE]

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
        health_payload = HealthPayload.from_bytes(transaction.payload)
        health_state = HealthState(context)

        if health_payload.txn_type == 'commit':
            self.count_access += 1
            active_transaction = HealthTransaction(
                txn_type=health_payload.txn_type,
                txn_id=health_payload.txn_id,
                data=health_payload.data,
                state=health_payload.state,
                url=health_payload.url,
                client_key=health_payload.client_key,
                txn_date=health_payload.txn_date)
            health_state.set_transaction(health_payload.txn_id, active_transaction)
            #call code analysis
            #the validator access the processor a couple of times, first to do a
            #kind of setup and second to publish the validated block
            #that's why6 we have a counter, we don't want to calculate the Health
            #each time. in the second time is when we know the block was validated
            if self.count_access == 2:
                self.count_access = 0
                print (health_payload.client_key)
                process_health(health_payload.txn_id, health_payload.data, health_payload.url, health_payload.txn_date, health_payload.client_key)
        elif health_payload.txn_type == 'health':
            active_transaction = HealthTransaction(
                txn_type=health_payload.txn_type,
                txn_id=health_payload.txn_id,
                data=health_payload.data,
                state=health_payload.state,
                url=health_payload.client_key,
                client_key=health_payload.client_key,
                txn_date=health_payload.txn_date)
            health_state.set_transaction(health_payload.txn_id, active_transaction)
        else:
            raise InvalidTransaction('Unhandled Type: {}'.format(health_payload.txn_type))

        _display("transaction {},{} created".
                 format(health_payload.txn_type, health_payload.data))

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
