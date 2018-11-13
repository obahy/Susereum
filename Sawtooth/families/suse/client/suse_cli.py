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
Suse Family Processor Command Line Interface

This processor handles all transaction related to the commit of suse and healt scores,
after processing the health, the new health is send to the suse family.

Raises:
    suse exceptions: suse family exceptions to display misuse of functions
"""
from __future__ import print_function

import os
import sys
import getpass
import logging
import argparse
import traceback

from colorlog import ColoredFormatter #pylint: disable=import-error
from client.suse_client import SuseClient
from client.suse_exceptions import SuseException

DISTRIBUTION_NAME = 'susereum-suse'
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
    define subparser list. Displays user's suse

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'list',
        help='Display suse ',
        description='Display users suse',
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

def add_create_parser(subparser, parent_parser):
    """
    add subparser default. this subparser will create suse based on the new  health

    Args:
        subparser (subparser): subparser handler
        parent_parser (parser): parent parser
    """
    parser = subparser.add_parser(
        'create',
        help='Create suse',
        description='Generate suse from commit',
        parents=[parent_parser])

    parser.add_argument(
        '--health',
        type=str,
        help='New Health')

    parser.add_argument(
        '--gituser',
        type=str,
        help='specify user github ID')

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
    add_create_parser(subparsers, parent_parser)
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
    client = SuseClient(base_url=url, keyfile=keyfile, work_path=HOME)

    transactions = client.list()

    if len(transactions) == 0:
        raise SuseException("No transactions found")
    else:
        print (transactions)


def do_create(args):
    """
    create suse of new commit

    Args:
        args (array) arguments
    """
    if args.health is None:
        raise SuseException("Missing health")
    if args.gituser is None:
        raise SuseException("Missing User ID")

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = SuseClient(base_url=url, keyfile=keyfile, work_path=HOME)

    response = client.create(new_health=args.health, github_id=args.gituser)

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

    #Define suse family functions
    if args.command == 'create':
        do_create(args)
    elif args.command == 'list':
        do_list(args)
    else:
        raise SuseException("Invalid command: {}".format(args.command))

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
    except SuseException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
