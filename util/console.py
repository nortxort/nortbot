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

from datetime import datetime, date

import util.file_handler


try:
    # try importing optional module.
    from colorama import init, Style, Fore

    init(autoreset=True)

    class Color(object):
        """
        Predefined colorama colors.
        """
        RED = Fore.RED
        GREEN = Fore.GREEN
        YELLOW = Fore.YELLOW
        CYAN = Fore.CYAN
        MAGENTA = Fore.MAGENTA
        BLUE = Fore.BLUE
        WHITE = Fore.WHITE

        B_RED = Style.BRIGHT + RED
        B_GREEN = Style.BRIGHT + GREEN
        B_YELLOW = Style.BRIGHT + YELLOW
        B_CYAN = Style.BRIGHT + CYAN
        B_MAGENTA = Style.BRIGHT + MAGENTA
        B_BLUE = Style.BRIGHT + BLUE

        RESET = Style.RESET_ALL

except ImportError:

    # importing failed, use dummies
    init = None
    Style = None
    Fore = None

    class Color(object):
        """
        Dummy class in case importing colorama failed.
        """
        RED = ''
        GREEN = ''
        YELLOW = ''
        CYAN = ''
        MAGENTA = ''
        BLUE = ''
        WHITE = ''

        B_RED = ''
        B_GREEN = ''
        B_YELLOW = ''
        B_CYAN = ''
        B_MAGENTA = ''
        B_BLUE = ''

        RESET = ''


class ChatLogger(object):

    file = None
    path = None

    @classmethod
    def set_path_and_name(cls, room, log_path):
        today = date.today()
        cls.file = '%s-%s-%s.log' % (today.day, today.month, today.year)
        cls.path = '%s/%s/logs/' % (log_path, room)

    @classmethod
    def write_chat_log(cls, text):
        util.file_handler.writer(cls.path, cls.file, text)


class Console(ChatLogger):
    """
    A class for reading and writing to console.
    """

    def __init__(self, room, log_path='', chat_logging=False,
                 clock_color='', use_colors=False, use24hour=True):

        self.room = room
        self.log_path = log_path
        self._chat_logging = chat_logging
        self._clock_color = clock_color
        self._console_colors = use_colors
        self._use24hour = use24hour

    def write(self, text, color='', ts=True):
        """
        Writes text to console.

        https://www.metachris.com/2015/11/python-tools-for-string-unicode-encoding-decoding-printing/

        :param text: The text to write.
        :type text: str
        :param color: Optional Color
        :type color: str
        :param ts: Show a timestamp before the text.
        :type ts: bool
        """
        time_stamp = ''
        if ts:
            time_stamp = '[%s] ' % _ts(self._use24hour)

        if self._console_colors:
            txt = '%s%s%s%s%s' % \
                  (self._clock_color, time_stamp, Color.RESET, color, text)
        else:
            txt = '%s%s' % (time_stamp, text)

        try:
            txt = txt.encode('UTF-8', 'replace')
        except UnicodeEncodeError:
            txt = '%s error encoding to console' % time_stamp
        finally:
            print(txt)

        if self._chat_logging:
            # chat logging
            ChatLogger.set_path_and_name(self.room, self.log_path)
            ChatLogger.write_chat_log('%s%s' % (time_stamp, text))


def _ts(as24hour=False):
    """
    Timestamp in the format HH:MM:SS

    NOTE: milliseconds is included for the 24 hour format.

    :param as24hour: Use 24 hour time format.
    :type as24hour: bool
    :return: A string representing the time.
    :rtype: str
    """
    now = datetime.now()

    fmt = '%I:%M:%S:%p'
    if as24hour:
        fmt = '%H:%M:%S:%f'

    ts = now.strftime(fmt)
    if as24hour:
        return ts[:-3]

    return ts
