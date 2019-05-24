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


class BannedUser(object):
    """
    Class representing a banned user.
    """

    def __init__(self, **kwargs):
        self._ban_id = kwargs.get('id', 0)
        self._nick = kwargs.get('nick', '')
        self._account = kwargs.get('username', None)
        self._banned_by = kwargs.get('moderator', '')
        self._reason = kwargs.get('reason', '')

    @property
    def ban_id(self):
        """
        The ban id of a banned user.

        NOTE: If a user is to be unbanned,
        this id is to be used.

        :return: The banned id.
        :rtype: int
        """
        return self._ban_id

    @property
    def nick(self):
        """
        The nick name of the user banned.

        :return: The nick of the banned user.
        :rtype: str
        """
        return self._nick

    @property
    def account(self):
        """
        The account of the banned of user.

        :return: The account name of the user.
        :rtype: str
        """
        return self._account

    @property
    def banned_by(self):
        """
        The name of the moderator who banned the user.

        :return: Name of the moderator the banned the user.
        :rtype: str
        """
        return self._banned_by

    @property
    def reason(self):
        """
        The reason for the ban.

        NOTE: This seems to not be implemented by tinychat yet.

        :return: The reason the user was banned.
        :rtype: str
        """
        return self._reason
