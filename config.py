# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2019 Nortxort

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import os
import sys

from ConfigParser import SafeConfigParser

# bot version
__version__ = '1.1.0.7'

# default config sections
CONFIG_SECTIONS = ['strings', 'booleans', 'integers']


class ConfigBaseError(Exception):
    """ Base config exception """
    pass


class MissingConfigFileError(BaseException):
    """ Raised if no config file is found on the given path. """
    pass


class MissingSectionError(BaseException):
    """ Raised if a needed section is missing. """
    pass


class UnsupportedReturnTypeError(BaseException):
    """ Raised when the return type is unsupported. """
    pass


class Config:
    """
    Class representing the config file.
    """
    def __init__(self, file_path='', file_name='config.ini'):
        """
        Initialize the Config class.

        :param file_path: The path to the config file.
        :type file_path: str
        :param file_name: The name of the config file.
        :type file_name: str
        """
        self._file_path = file_path
        self._file_name = file_name
        self._config = None
        self._sections = CONFIG_SECTIONS

    def load_file(self):
        """
        Load the config file.
        """
        parser = SafeConfigParser(allow_no_value=True)
        if self._file_path:
            parser_read = parser.read(self._file_path + '/' + self._file_name)
        else:
            parser_read = parser.read(self._file_name)
        if len(parser_read) is 0:
            raise MissingConfigFileError('`%s` not found in path `%s`' %
                                         (self._file_name, self._file_path))
        else:
            self._config = parser

    def has_sections(self):
        """
        Check if the config file has the required sections.
        """
        missing_sections = []
        for section in self._sections:
            has_section = self._config.has_section(section)
            if not has_section:
                missing_sections.append(section)

        if len(missing_sections) > 0:
            raise MissingSectionError('missing section(s) %s in %s' %
                                      (missing_sections, self._file_name))

    def get(self, section, option, default=None, rtype='str'):
        """
        Get the option value of a section.

        If a option has no value or if the value is of the wrong type,
        then the default value will be returned instead.

        :param section: The section for which to get the option from.
        :type section: str
        :param option: The name of the option to get the value from.
        :type option: str
        :param default: The default value to return if no option was found
        or is of the wrong type.
        :type default: str | int | float | bool | None
        :param rtype: The expected value type of the option.
        :type rtype: str
        :return: The specified option value.
        """
        return self._get(section=section, option=option, default=default, rtype=rtype)

    def print_config(self):
        """
        Print the sections and their option values to console.
        """
        if self._config is not None:
            for section_name in self._config.sections():
                # print ('Options: %s' % self._config.options(section_name))
                print('\nSection: %s' % section_name)
                for name, value in self._config.items(section_name):
                    print('    %s = %s' % (name, value))

    def _has_option(self, section, option):

        if self._config.has_option(section, option):
            return True
        return False

    def _get(self, section, option, default=None, rtype='str'):

        if self._has_option(section, option):

            if rtype == 'str':
                res = self._config.get(section, option, raw=True)
                if res == '':
                    return default
                return res

            elif rtype == 'int':
                try:
                    res = self._config.getint(section, option)
                except ValueError:
                    return default
                return res

            elif rtype == 'float':
                try:
                    res = self._config.getfloat(section, option)
                except ValueError:
                    return default
                return res

            elif rtype == 'bool':
                try:
                    res = self._config.getboolean(section, option)
                except ValueError:
                    return False
                return res

            else:
                raise UnsupportedReturnTypeError('the return type `%s` is not supported.' % rtype)

        return default


_errors = []
_application_path = ''


# check if we are an executable and set a path accordingly
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.system('title Nortbot ' + __version__)
    # in the case where we are an executable, we need to
    # tell requests and websocket client
    # where to find the cacert.pem file
    os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'
    os.environ['WEBSOCKET_CLIENT_CA_BUNDLE'] = 'cacert.pem'

# regular python file
elif __file__:
    application_path = os.path.dirname(__file__)

# initialize the config class with the default
# config file name (config.ini)
config = Config(file_path=_application_path)

try:
    # try loading the config file
    config.load_file()
except MissingConfigFileError as e:
    _errors.append(e)
else:
    try:
        # check if the config has the required sections
        config.has_sections()
    except MissingSectionError as mse:
        _errors.append(mse)

if len(_errors) > 0:

    for error in _errors:
        print(error)

    raw_input('\nfix the error(s) and click enter to close the application.')
    sys.exit(1)

# Config
ROOM = config.get('strings', 'Room')
NICK = config.get('strings', 'Nick')
ACCOUNT = config.get('strings', 'Account')
PASSWORD = config.get('strings', 'Password')
ANTI_CAPTCHA_KEY = config.get('strings', 'AntiCaptchaKey')
WEATHER_KEY = config.get('strings', 'WeatherApiKey')
FALLBACK_RTC_VERSION = config.get(
    'strings', 'FallbackRtcVersion', default='2.0.22-4')
CHAT_LOGGING = config.get('booleans', 'ChatLogging', rtype='bool')
DEBUG_MODE = config.get('booleans', 'DebugMode', rtype='bool')
DEBUG_TO_FILE = config.get('booleans', 'DebugToFile', rtype='bool')
DEBUG_LEVEL = config.get('integers', 'DebugLevel', default=30, rtype='int')
CONSOLE_COLORS = config.get('booleans', 'ConsoleColors', rtype='bool')
USE_24HOUR = config.get('booleans', 'Use24Hour', rtype='bool')
DEBUG_FILE_NAME = config.get('strings', 'DebugFileName', default='debug.log')
CONFIG_PATH = config.get('strings', 'ConfigPath', default='rooms/')
THREAD_POOL = config.get('integers', 'ThreadPool', default=10, rtype='int')
# these used to have the B prefix
BOT_VERSION = __version__
PREFIX = config.get('strings', 'Prefix', default='!')
KEY = config.get('strings', 'Key', default='hsd87fs7')
SUPER_KEY = config.get('strings', 'SuperKey', default='8ssfy7723avf')
MAX_MATCH_BANS = config.get('integers', 'MaxMatchBans', default=2, rtype='int')
MAX_NOTIFY_DELAY = config.get(
    'integers', 'MaxNotifyDelay', default=2, rtype='int')
PUBLIC_CMD = config.get('booleans', 'PublicCmd', rtype='bool')
GREET = config.get('booleans', 'Greet', rtype='bool')
AUTO_LOGIN = config.get('booleans', 'AutoLogin', rtype='bool')
ALLOW_GUESTS = config.get('booleans', 'AllowGuests', rtype='bool')
ALLOW_LURKERS = config.get('booleans', 'AllowLurkers', rtype='bool')
ALLOW_GUESTS_NICKS = config.get('booleans', 'AllowGuestsNicks', rtype='bool')
USE_KICK_AS_AUTOBAN = config.get('booleans', 'KickAsAutoban', rtype='bool')
VIP_MODE = config.get('booleans', 'VipMode', rtype='bool')
ENABLE_VOTING = config.get('booleans', 'EnableVoting', rtype='bool')
TRY_TIME_BASED_CHECKS = config.get(
    'booleans', 'TryTimeBasedCheck', rtype='bool')
NOTIFY_ON_BAN = config.get('booleans', 'NotifyOnBan', rtype='bool')
APPROVED_FILE_NAME = config.get(
    'strings', 'ApprovedFileName', default='approved_accounts.txt')
NICK_BANS_FILE_NAME = config.get(
    'strings', 'NickBansFileName', default='nick_bans.txt')
ACCOUNT_BANS_FILE_NAME = config.get(
    'strings', 'AccountBansFileName', default='account_bans.txt')
STRING_BANS_FILE_NAME = config.get(
    'strings', 'StringBansFileName', default='string_bans.txt')
APPROVED = []
ACCOUNT_BANS = []
NICK_BANS = []
STRING_BANS = []
