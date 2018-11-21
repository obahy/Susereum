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
Health Family Processor Command Line Interface

This processor handles all transaction related to the commit of new code,
whenever users made a commit to github this class will trigger logic to process
the commit and calculate project's health.

Raises:
    health exceptions: health family exceptions to display misuse of functions
"""
from __future__ import print_function

import os
import sys
import getpass
import logging
import argparse
import traceback

from colorlog import ColoredFormatter #pylint: disable=import-error
from client.health_client import HealthClient
from client.health_exceptions import HealthException

DISTRIBUTION_NAME = 'susereum-health'
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


def add_list_parser(subparser, parent_parser):
    """
    define subparser list. Displays information for all health transactions

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'list',
        help='Displays information for all health transactions',
        description='Displays information for all health trasactions in state',
        parents=[parent_parser])

    parser.add_argument(
        '--type',
        type=str,
        help='Display specific type of transaction')

    parser.add_argument(
        '--limit',
        type=str,
        help='limit number of transaction to look for transactions')

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

def add_commit_parser(subparser, parent_parser):
    """
    add subparser default. this subparser will create a commit transaction that
        will be send to the code analysis

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'commit',
        help='Process commit',
        description='Send commit to code analysis',
        parents=[parent_parser])

    parser.add_argument(
        '--giturl',
        type=str,
        help='specify commit URL')

    parser.add_argument(
        '--gituser',
        type=str,
        help='specify user github ID')

    parser.add_argument(
        '--date',
        type=str,
        help='commit date')

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
        '--client_key',
        type=str,
        help="key to identify client")

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
        description='Suserum custom family (health) to process and manage commit transactions.',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True
    add_commit_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)

    return parser


def do_list(args):
    """
    list transactions of code smell family

    Args:
        args (array) arguments
    """
    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = HealthClient(base_url=url, keyfile=keyfile, work_path=HOME)

    if args.limit is None:
        transactions = client.list(txn_type=args.type)
    else:
        transactions = client.list(txn_type=args.type, limit=args.limit)

    if len(transactions) == 0:
        raise HealthException("No transactions found")
    else:
        print (transactions)

def process_health(github_user, github_url, url, commit_date, client_key):
    """
    Process commit, send url to code analysis
    """
    keyfile = _get_keyfile()
    client = HealthClient(base_url=url, keyfile=keyfile, work_path=HOME)

    response = client.code_analysis(github_url, github_user, commit_date, client_key)

    print("Response: {}".format(response))


def do_commit(args):
    """
    load a set of default code smells.

    Args:
        args (array) arguments
    """
    if args.giturl is None:
        raise HealthException("Missing Commit URL")
    if args.gituser is None:
        raise HealthException("Missing User ID")
    if args.date is None:
        raise HealthException("Missing Commit Date")
    if args.client_key is None:
        raise HealthException("Missing Client Key")


    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = HealthClient(base_url=url, keyfile=keyfile, work_path=HOME)

    response = client.commit(commit_url=args.giturl, github_id=args.gituser, commit_date=args.date, client_key=args.client_key)

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

def _get_keyfile(args=None):
    """
    Retrives user's private key directory.
    Each transaction should be sign by the user who create it.

    Args:
        args (array): private key username

    Returns:
        str: path of user's private key
    """
    if args is None:
        username = getpass.getuser()
    else:
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

    #Define health family functions
    if args.command == 'commit':
        do_commit(args)
    elif args.command == 'list':
        do_list(args)
    else:
        raise HealthException("Invalid command: {}".format(args.command))

def main_wrapper():
    """
    Wrapper to main function.

    Args:
        None

    Exceptions:
        HealthException
        KeyboardInterrupt
        BaseException
    """
    try:
        main()
    except HealthException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
