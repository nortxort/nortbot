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

import random
import re
from web import quote, unquote


def is_valid_string(input_str, pattern='^[a-zA-Z0-9]*$'):
    """
    Check a string to see if it is valid based on the pattern.

    :param input_str: The string to check.
    :type input_str: str
    :param pattern: The pattern to check the string against.
    :type pattern: str
    :return: True if its a valid string.
    :rtype: bool
    """
    if re.match(pattern, input_str):
        return True
    return False


def quote_str(input_str, safe=':,./&+?#=@'):
    """
    Quote a string.

    :param input_str: The input string.
    :type input_str: str
    :param safe: Characters not to be quoted.
    :type safe: str
    :return: A quoted string.
    :rtype: str
    """
    return quote(input_str, safe=safe)


def unquote_str(input_str):
    """
    Unquote a string.

    :param input_str: Input string to unquote.
    :type input_str: str
    :return: Unquoted string.
    :rtype: str
    """
    return unquote(input_str)


def chunk_string(input_str, length):
    """
    Splits a string in to smaller chunks.
    NOTE: http://stackoverflow.com/questions/18854620/

    :param input_str: The input string to chunk.
    :type input_str: str
    :param length: The length of each chunk.
    :type length: int
    :return: A list of the input string as smaller chunks.
    :rtype: list
    """
    return list((input_str[0 + i:length + i] for i in range(0, len(input_str), length)))


def create_random_string(min_length, max_length, numbers=True,
                         upper=False, other=False):
    """
    Creates a random string of letters and numbers.

    For a fixed length, set min_length to the same as max_length.

    :param min_length: Minimum length of the string.
    :type min_length: int
    :param max_length: Maximum length of the string.
    :type max_length: int
    :param numbers: Include numbers.
    :type numbers: bool
    :param upper: Include upper case letters.
    :type upper: bool
    :param other: Include other characters.
    :type other: bool
    :return: A random string of letters and optionally numbers,
    upper case letters and other characters.
    :rtype: str
    """
    if min_length > max_length:
        raise ValueError('min_length cannot be > max_length.')

    if min_length == max_length:
        length = min_length
    else:
        length = random.randint(min_length, max_length)

    junk = 'abcdefghijklmnopqrstuvwxyz'
    if numbers:
        junk += '0123456789'
    if upper:
        junk += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if other:
        junk += '!"#&/()=?`;:,_-~|%&@£$€{[]}<>'

    return ''.join((random.choice(junk) for _ in xrange(length)))


def convert_to_seconds(duration):
    """
    Converts a ISO 8601 unicode duration string to seconds.

    :param duration: The ISO 8601 unicode duration string.
    :return: Seconds as integer.
    """
    duration_string = duration.replace('PT', '').upper()
    seconds = 0
    number_string = ''

    for char in duration_string:
        if char.isnumeric():
            number_string += char
        try:
            if char == 'H':
                seconds += (int(number_string) * 60) * 60
                number_string = ''
            if char == 'M':
                seconds += int(number_string) * 60
                number_string = ''
            if char == 'S':
                seconds += int(number_string)
        except ValueError:
            return 0
    return seconds
