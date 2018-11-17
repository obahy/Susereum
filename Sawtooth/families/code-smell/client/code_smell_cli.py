# Copyright 2017 Intel Corporation
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
# ------------------------------------------------------------------------------
"""
code smell command line interface.
"""
## TODO: research if peers will require a username and password to join the network

from __future__ import print_function

import os
import sys
import toml
import getpass
import logging
import argparse
import traceback
import pkg_resources

from colorlog import ColoredFormatter #pylint: disable=import-error
from pprint import pprint
from argparse import RawTextHelpFormatter
from client.code_smell_client import CodeSmellClient
from client.code_smell_exceptions import CodeSmellException

DISTRIBUTION_NAME = 'suserum-code_smell'
HOME = os.getenv('SAWTOOTH_HOME')
DEFAULT_URL = 'http://127.0.0.1:8008'

def create_console_handler(verbose_level):
    """
    Create console handler, defines logging level

    Args:
        verbose_level (int): argument passed by user defining if verbose will be active

    Returns:
        clog: console handler to display verbose output
    """

    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG'    : 'cyan',
            'INFO'     : 'green',
            'WARNING'  : 'yellow',
            'ERROR'    : 'red',
            'CRITICAL' : 'red',
        })
    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog

def setup_loggers(verbose_level):
    """
    Set up level of verbose.

    Args:
        verbose_level (int): argument passed by user defining if verbose will be active
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def add_show_parser(subparser, parent_parser):
    """
    define subparser show. show an specific component (code smells, proposals, votes)

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'show',
        help='Display transaction',
        description='Display an specific component of the code smell family',
        parents=[parent_parser])

    parser.add_argument(
        '--address', '-a',
        type=str,
        help='Address of asset')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

def add_vote_parser(subparser, parent_parser):
    """
    define subparser vote. vote to proposals

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'vote',
        help='Vote on Proposal',
        description='cast a vote to accep or reject a proposal',
        parents=[parent_parser])

    parser.add_argument(
        '--id',
        type=str,
        help='Vote to <proposal_id>')

    parser.add_argument(
        '--vote',
        type=str,
        help='accept (yes) or reject (no) proposal')

    parser.add_argument(
        '--view',
        type=str,
        help='view number of votes')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

def add_proposal_parser(subparser, parent_parser):
    """
    define subparser proposal. request a new proposal to update code smell configutation

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'proposal',
        help='Request a change in the current code smell configuration',
        description='Request a change in the current code smell configuration \n'
                    'list of code smells and metrics {<code smell=metric>,<code smell=metric> }',
        formatter_class=RawTextHelpFormatter,
        parents=[parent_parser])

    parser.add_argument(
        '--propose', '-p',
        type=str,
        help='Request a change in the current code smell configuration')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

def add_list_parser(subparser, parent_parser):
    """
    define subparser list. Displays information for all code smells

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'list',
        help='Displays information for all code smells transactions',
        description='Displays information for all code smells in state',
        parents=[parent_parser])

    parser.add_argument(
        '--type',
        type=str,
        help='Display only one type of transactions')

    # parser.add_argument(
    #     '--active',
    #     type=str,
    #     help='Display onle active proposals')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

def add_default_parser(subparser, parent_parser):
    """
    add subparser default. this subparser will load a
        default configuration for the code_smell family.

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'default',
        help='Load Default Configuration',
        description='Send transaction to load default configuration',
        parents=[parent_parser])

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--key-dir',
        type=str,
        help="identify directory of user's private key file")

    parser.add_argument(
        '--path',
        type=str,
        default=HOME,
        help="working directory")

    parser.add_argument(
        '--disable-client-valiation',
        action='store_true',
        default=False,
        help='disable client validation')

def create_parent_parser(prog_name):
    """
    Create parent parser

    Args:
        prog_name (str): program name

    Returns:
        parser: parent argument parser

    Raises:
        DistributionNotFound: version of family not found

    """
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    return parent_parser

def create_parser(prog_name):
    """
    Function to create parent parser as well as subparsers.

    Args:
        prog_name (str): program name

    Returns:
        parser
    """
    parent_parser = create_parent_parser(prog_name)

    #create subparser, each subparser requires a different set of arguments.
    parser = argparse.ArgumentParser(
        description=
        'Suserum custom family (code_smell) to process and manage code smell transactions.',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True
    add_default_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)
    add_proposal_parser(subparsers, parent_parser)
    add_show_parser(subparsers, parent_parser)
    add_vote_parser(subparsers, parent_parser)

    return parser

def do_show(args):
    """
    list transaction of code smell family

    Args:
        args (array) arguments
    """
    if args.address is None:
        raise CodeSmellException("Missing Transaction Address")

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = CodeSmellClient(base_url=url, keyfile=keyfile, work_path=HOME)

    transaction = client.show(address=args.address)

    if len(transaction) == 0:
        raise CodeSmellException("No transaction found")
    else:
        pprint(transaction)

def do_vote(args):
    """
    cast vote to accept or reject a code measure proposal

    Args:
        args (array) arguments<proposalid, vote>
    """
    if args.view is None:
        if args.id is None:
            raise CodeSmellException("Missing proposal ID")
        if args.vote is None:
            raise CodeSmellException("Missing VOTE")
        if args.vote == 'yes':
            vote = 1
        else:
            vote = 0

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = CodeSmellClient(base_url=url, keyfile=keyfile, work_path=HOME)

    if args.vote:
        response_dict = client.vote(proposal_id=args.id, vote=vote)
        print("Response: {}".format(response_dict))
        #return response_dict
    else:
        response_list = client.check_votes(proposal_id=args.view)
        #return response_list
        print("Response: {}".format(response_list))

def do_proposal(args):
    """
    propose new metric for the code smell family

    Args:
        args (array) arguments
    """

    if args.propose is None:
        raise CodeSmellException("Missing code smells")

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = CodeSmellClient(base_url=url, keyfile=keyfile, work_path=HOME)

    #parse input into a dict
    code_smells = {}
    str_input = args.propose
    code_smells = dict(code_smell.split("=") for code_smell in str_input.split(","))

    response = client.propose(code_smells=code_smells)

    print("Response: {}".format(response))

def do_list(args):
    """
    list transactions of code smell family

    Args:
        args (array) arguments
    """
    #verify that we shave the right type
    if args.type is not None and args.type not in ('code_smell', 'proposal', 'vote', 'config'):
        raise CodeSmellException("Incorrect Transaction Type")
    # if args.type in ('code_smell', 'vote') and args.active is not None:
    #     raise CodeSmellException("Incorrect parms combination")

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = CodeSmellClient(base_url=url, keyfile=keyfile, work_path=HOME)

    # if args.active is not None:
    #     transactions = client.list(txn_type=args.type, active_flag=1)
    # else:
    transactions = client.list(txn_type=args.type)

    if len(transactions) == 0:
        raise CodeSmellException("No transactions found")
    else:
        print (transactions)

def do_default(args):
    """
    load a set of default code smells.

    Args:
        args (array) arguments
    """
    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = CodeSmellClient(base_url=url, keyfile=keyfile, work_path=args.path)

    response = client.default()

    print("Response: {}".format(response))

def _get_url(args):
    """
    Pull rest_api url, use default if user does not specify

    Args:
        args (array): arguments from parser

    Returns:
        str: url of rest_api

    """
    return DEFAULT_URL if args.url is None else args.url

def _get_keyfile(args):
    """
    Retrives user's private key directory.
    Each transaction should be sign by the user who create it.

    Args:
        args (array): private key username

    Returns:
        str: path of user's private key
    """

    username = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    """
    Expose core functionality of the code_smell family.

    Args:
        prog_name, program name (str)
        args, arguments to process code smells (array)
    """
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    #Define code smell family functions
    if args.command == 'default':
        do_default(args)
    elif args.command == 'list':
        do_list(args)
    elif args.command == 'proposal':
        do_proposal(args)
    elif args.command == 'show':
        do_show(args)
    elif args.command == 'vote':
        do_vote(args)
    else:
        raise CodeSmellException("Invalid command: {}".format(args.command))

def main_wrapper():
    """
    Wrapper to main function.

    Args:
        None

    Exceptions:
        codeSmellException
        KeyboardInterrupt
        BaseException
    """
    try:
        main()
    except CodeSmellException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
