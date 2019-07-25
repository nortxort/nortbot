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

import logging

from check import Check
from apis import TinychatApi
from util.console import Color

log = logging.getLogger(__name__)


class JoinHandler(Check):
    def __init__(self, bot, user, config):
        super(JoinHandler, self).__init__(bot, user, config)
        self._bot = bot
        self._user = user
        self._conf = config

    def handle(self):
        """
        Handle a join event.
        """
        log.info('handling join for: %s' % self._user)

        if self._user.account is not None:

            if self._user.is_mod:
                self._add_tc_info()
                self._greet()

            elif self._user.account in self._conf.APPROVED:  # and not self._user.is_mod
                self._add_tc_info()
                self._set_approved()
                self._greet()
            else:
                if not Check.account(self) and not Check.vip_mode(self):
                    if not Check.nick(self):
                        self._add_tc_info()
                        self._greet()
        else:
            if not Check.guest_entry(self) and not Check.lurker(self) \
                    and not Check.vip_mode(self):

                if not Check.nick(self):
                    self._greet()

    def console(self):
        """
        Write the join event to console.
        """
        if self._user.is_owner:
            self._bot.console.write('Owner joined: %s:%s:%s' %
                                    (self._user.nick, self._user.handle,
                                     self._user.account), Color.B_BLUE)
        elif self._user.is_mod:
            self._bot.console.write('Moderator joined: %s:%s:%s' %
                                    (self._user.nick, self._user.handle,
                                     self._user.account), Color.B_RED)
        elif self._user.account is not None:
            self._bot.console.write('User joined: %s:%s:%s' %
                                    (self._user.nick, self._user.handle,
                                     self._user.account), Color.B_GREEN)
        else:
            self._bot.console.write('Guest joined: %s:%s' %
                                    (self._user.nick, self._user.handle),
                                    Color.B_YELLOW)

    def _greet(self):
        # TODO: greet based on user roles?
        if self._conf.GREET:
            if not self._user.nick.startswith('guest-'):

                if self._user.account is not None:
                    # using responder with timeout
                    self._bot.responder('Welcome to the room %s:%s:%s' %
                                        (self._user.nick, self._user.account,
                                         self._user.handle),
                                        timeout=self._bot.rand_float())
                else:
                    self._bot.responder('Welcome to the room %s:%s' %
                                        (self._user.nick, self._user.handle),
                                        timeout=self._bot.rand_float())

    def _add_tc_info(self):
        log.debug('adding tinychat info for user: %s' % self._user)
        tc_info = TinychatApi.user_info(self._user.account)
        if tc_info is not None:
            self._bot.users.add_tc_info(self._user.handle, tc_info)

    def _set_approved(self):
        if not self._user.is_owner or not self._user.is_mod:
            log.debug('setting user level to approved: %s' % self._user)
            self._bot.users.mark_as_approved(self._user.handle)
