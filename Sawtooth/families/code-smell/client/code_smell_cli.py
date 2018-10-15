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

from colorlog import ColoredFormatter
from pprint import pprint
from code_smell_client import codeSmellClient
from code_smell_exceptions import codeSmellException

DISTRIBUTION_NAME = 'sawtooth-code_smell'
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
        help='Vote Proposal',
        description='vote to a specific proposal',
        parents=[parent_parser])

    parser.add_argument(
        '--proposalID',
        type=str,
        help='Vote to <proposal_id>')

    parser.add_argument(
        '--accept',
        type=str,
        help='Accept proposal')

    parser.add_argument(
        '--reject',
        type=str,
        help='Reject proposal')

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
        description='Request a change in the current code smell configuration',
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
        '--disable-client-valiation',
        action='store_true',
        default=False,
        help='disable client validation')

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        #default=30, ## TODO: update this value to something appropiate
        help='set time, in seconds, to wait for code smell to commit')

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

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}').format(version),
        help='display version information')

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

    """create subparser, each subparser requires a different set of arguments."""
    parser = argparse.ArgumentParser(
        description='Suserum custom family (code_smell) to process and manage code smell transactions.',
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
    print ("show")
def do_vote(args):
    print ("vote")
def do_proposal(args):
    print ("proposal")
def do_list(args):
    """
    list transactions of code smell family

    Args:
        args (array) arguments
    """
    if args.type is not None and args.type not in ('code_smell', 'proposal', 'vote'):
            raise codeSmellException ("Incorrect Transaction Type")
    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = codeSmellClient(base_url=url, keyfile=keyfile, work_path=HOME)

    transctions = client.list(type=args.type)

    if len(transctions) == 0:
        raise codeSmellException("No transactions found")
    else:
        print (transctions)

def do_default(args):
    """
    load a set of default code smells.

    Args:
        args, arguments (array)
    """
    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = codeSmellClient(base_url=url, keyfile=keyfile, work_path=HOME)

    if args.wait and args.wait > 0:
        response = client.default(wait=args.wait)
    else:
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
        args=sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    """Define code smell family functions"""
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
        raise codeSmellException("Invalid command: {}".format(args.command))

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
    except codeSmellException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
