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

from datetime import datetime
from user_level import UserLevel


class User(object):
    """
    Class representing a tinychat room user.
    """
    def __init__(self, **kwargs):
        self.location = None
        self.nick = kwargs.get('nick', '')
        self.age = None
        self.gender = None
        self.role = None
        self.biography = None
        self.gift_points = kwargs.get('giftpoints', 0)
        self.featured = kwargs.get('featured', False)               # ?
        self.subscription = kwargs.get('subscription', 0)           # ?
        self.achievement_url = kwargs.get('achievement_url', '')    # ?
        self.avatar = kwargs.get('avatar', '')                      # ?
        self.is_broadcasting = False
        self.can_broadcast = True
        self.is_waiting = False
        self.old_nicks = [self.nick]

        self.nick_time = 0  # not implemented

        self.messages = []

        self._handle = kwargs.get('handle')                 # readonly
        self._account = kwargs.get('username', None)        # readonly
        self._session_id = kwargs.get('session_id', '')     # readonly
        self._is_lurker = kwargs.get('lurker', False)       # readonly
        self._is_mod = kwargs.get('mod', False)             # readonly
        self._is_owner = kwargs.get('owner', False)         # readonly
        self._join_time = datetime.now()                    # readonly

        if self._account == '':
            self._account = None

        if self.is_owner:
            self.level = UserLevel.OWNER
        elif self.is_mod:
            self.level = UserLevel.MODERATOR
        else:
            self.level = UserLevel.DEFAULT

    def __repr__(self):
        return '<%s nick=%s, handle=%s, account=%s, ' \
               'is_owner=%s, is_mod=%s, level=%s, ' \
               'join_time=%s' % (self.__class__.__name__,
                                 self.nick, self.handle,
                                 self.account, self.is_owner,
                                 self.is_mod, self.level, self.join_time)

    @property
    def handle(self):
        """
        The handle of a user.

        :return: The handle of a user.
        :rtype: int
        """
        return self._handle

    @property
    def account(self):
        """
        The account of a user.

        :return: The account name of a user.
        :rtype: str
        """
        return self._account

    @property
    def session_id(self):
        """
        The session id of a user.

        :return: The user's session id.
        :rtype: str
        """
        return self._session_id

    @property
    def is_lurker(self):
        """
        Indicating if the user is a lurker.

        :return: True if the user is a lurker.
        :rtype: bool
        """
        return self._is_lurker

    @property
    def is_mod(self):
        """
        Indicating is the user is a moderator.

        :return: True if the user is a moderator.
        :rtype: bool
        """
        return self._is_mod

    @property
    def is_owner(self):
        """
        Indicating if the user is the owner.

        :return: True if the user is the owner of the room.
        :rtype: bool
        """
        return self._is_owner

    @property
    def join_time(self):
        """
        The time stamp the user joined the room at.

        NOTE: when joining the room, user currently
        in the room will have the same timestamp.

        :return: The timestamp as datetime object.
        :rtype: datetime
        """
        return self._join_time

    @property
    def last_msg(self):
        """
        Return the last message of a user.

        :return: The last message sent by a user.
        :rtype: str
        """
        if len(self.messages) > 0:
            if self.messages[-1].type == 3:
                return self.messages[-1].title
            elif self.messages[-1].type == 2:
                return 'Not showing PM.'
            else:
                return self.messages[-1].text
        return ''

    @property
    def last_nick(self):
        """
        Return the last used nick of a user.

        :return: Last used nick of a user.
        :rtype: str
        """
        if len(self.old_nicks) > 1:
            return self.old_nicks[-2]
        return self.nick
