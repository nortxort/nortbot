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
from util.console import Color

log = logging.getLogger(__name__)


class NickHandler(Check):
    def __init__(self, bot, user, config):
        super(NickHandler, self).__init__(bot, user, config)
        self._bot = bot
        self._user = user
        self._conf = config

    def handle(self):
        """
        Handle a nick event.
        """
        log.info('handling nick for: %s' % self._user)

        # do not check moderators for bad nicks
        # since we cant ban them anyway.
        if not self._user.is_mod:
            if not Check.nick(self):
                self._greet()
        else:
            self._greet()

    def console(self):
        """
        Write the nick event to console.
        """
        if self._user.handle == self._bot.users.client.handle:
            self._bot.console.write('The bot changed nick to %s' %
                                    self._user.nick, Color.GREEN)
        else:
            self._bot.console.write('%s:%s changed nick to %s' %
                                    (self._user.last_nick, self._user.handle,
                                     self._user.nick), Color.B_CYAN)

    def _greet(self):
        # TODO: greet based on user roles?
        if self._user.handle != self._bot.users.client.handle:
            if self._conf.GREET:
                if self._user.last_nick.startswith('guest-'):

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
