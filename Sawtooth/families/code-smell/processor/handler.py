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
code smell family handler, process and verifies that transaction's payload is correct
"""
import logging

from sawtooth_sdk.processor.exceptions import InvalidTransaction #pylint: disable=import-error
from sawtooth_sdk.processor.handler import TransactionHandler #pylint: disable=import-error

from processor.code_smell_state import CodeSmellTransaction
from processor.code_smell_state import CodeSmellState
from processor.code_smell_state import CODESMELL_NAMESPACE
from processor.code_smell_payload import CodeSmellPayload

LOGGER = logging.getLogger(__name__)

class CodeSmellTransactionHandler(TransactionHandler):
    """
    process all types of transactions regarding the code smell family
    """

    @property
    def family_name(self):
        """
        returns family name

        Returns:
            code_smell: family name
        """
        return 'code-smell'

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
        return [CODESMELL_NAMESPACE]

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
        code_smell_payload = CodeSmellPayload.from_bytes(transaction.payload)
        code_smell_state = CodeSmellState(context)

        if code_smell_payload.trac_type == 'code_smell':
            active_transaction = CodeSmellTransaction(
                trac_type=code_smell_payload.trac_type,
                trac_id=code_smell_payload.trac_id,
                data=code_smell_payload.data,
                state=code_smell_payload.state)
        elif code_smell_payload.trac_type == 'proposal':
            active_transaction = CodeSmellTransaction(
                trac_type=code_smell_payload.trac_type,
                trac_id=code_smell_payload.trac_id,
                data=code_smell_payload.data,
                state=code_smell_payload.state,
                date=code_smell_payload.date)
        elif code_smell_payload.trac_type == 'vote':
            active_transaction = CodeSmellTransaction(
                trac_type=code_smell_payload.trac_type,
                trac_id=code_smell_payload.trac_id,
                data=code_smell_payload.data,
                state=code_smell_payload.state)
        else:
            raise InvalidTransaction('Unhandled Type: {}'.format(code_smell_payload.trac_type))

        code_smell_state.set_transaction(code_smell_payload.trac_id, active_transaction)

        _display("transaction {},{} created".
                 format(code_smell_payload.trac_type, code_smell_payload.data))

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
