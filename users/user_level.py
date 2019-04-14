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


class UserLevel(object):
    """
    User levels for users and the client.
    """
    # This level is reserved for the client itself.
    CLIENT = 0

    # This level is for the room owner. Or it can be
    # assigned to a user who has provided the correct super key
    # but *ONLY* if the bot is using the room owner account.
    OWNER = 1

    # This level is assigned to a user who has provided the
    # correct key.
    SUPER = 2

    # This level is for room moderators.
    MODERATOR = 3

    # This level is for approved accounts.
    APPROVED = 4

    # This level is for bot operators.
    # Users can be assigned this level, by user level 1,2 and 3
    BOT_OP = 5

    # This is the default user level.
    DEFAULT = 6
