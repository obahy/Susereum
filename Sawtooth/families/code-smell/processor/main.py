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
main program, process the code smell family logic.
"""
import sys
import argparse

from sawtooth_sdk.processor.config import get_log_dir #pylint: disable=import-error
from sawtooth_sdk.processor.log  import log_configuration #pylint: disable=import-error
from sawtooth_sdk.processor.log  import init_console_logging #pylint: disable=import-error
from sawtooth_sdk.processor.core import TransactionProcessor #pylint: disable=import-error
from processor.handler import CodeSmellTransactionHandler
from processor.code_smell_exceptions import CodeSmellException

DISTRIBUTION_NAME = 'sawtooth-codeSmell'

def parse_args(args):
    """
    Parse Arguments.

    Args:
        args (*args): Program Arguments

    Returns:
        args: list of arguments

    Raises:
        None
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-C', '--connect',
        default='tcp://localhost:4004',
        help='Endpoint for the validator connection')

    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase output sent to stderr')

    return parser.parse_args(args)

def main(args=None):
    """
    Main.

    Raises:
    RunTimeException, connection error
    """

    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    processor = None
    try:
        processor = TransactionProcessor(url=opts.connect)

        log_dir = get_log_dir()
        #use the transaction processor zmq idenity for filename
        log_configuration(
            log_dir=log_dir,
            name="code_smell-" + str(processor.zmq_id)[2:-1])

        init_console_logging(verbose_level=opts.verbose)

        handler = CodeSmellTransactionHandler()

        processor.add_handler(handler)

        processor.start()
    except KeyboardInterrupt:
        pass
    except RuntimeError as err:
        raise CodeSmellException("Error: {}".format(err))
    finally:
        if processor is not None:
            processor.stop()
