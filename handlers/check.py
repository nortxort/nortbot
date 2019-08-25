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
import datetime


log = logging.getLogger(__name__)


class Check(object):
    """
    Class for checking against the different ban settings.
    """
    def __init__(self, bot, user, config, msg=None):
        self._bot = bot
        self._user = user
        self._conf = config
        self._msg = msg

    def account(self):
        """
        Check account against account bans.

        :return: True if in the account was banned.
        :rtype: bool
        """
        log.debug('checking account for %s' % self._user)
        if self._user.account is not None and \
                self._user.account in self._conf.ACCOUNT_BANS:

            if self._conf.USE_KICK_AS_AUTOBAN:
                self._bot.send_kick_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Kicked: (account not allowed)',
                                        timeout=self._bot.rand_float())
            else:
                self._bot.send_ban_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Banned: (account not allowed)',
                                        timeout=self._bot.rand_float())

            return True

        return False

    def guest_entry(self):
        """
        Check a user against guest entry setting.

        :return: True if banned.
        :rtype: bool
        """
        log.debug('checking guest entry for %s' % self._user)
        if self._user.account is None and not self._conf.ALLOW_GUESTS:

            if self._conf.USE_KICK_AS_AUTOBAN:
                self._bot.send_kick_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Kicked: (guests not allowed)',
                                        timeout=self._bot.rand_float())
            else:
                self._bot.send_ban_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Banned: (guests not allowed)',
                                        timeout=self._bot.rand_float())

            return True

        return False

    def lurker(self):
        """
        Check a user against the lurker setting.

        :return: True if banned.
        :rtype: bool
        """
        log.debug('checking lurker for %s' % self._user)
        if self._user.is_lurker and not self._conf.ALLOW_LURKERS:

            if self._conf.USE_KICK_AS_AUTOBAN:
                self._bot.send_kick_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Kicked: (lurkers not allowed)',
                                        timeout=self._bot.rand_float())
            else:
                self._bot.send_ban_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Banned: (lurkers not allowed)',
                                        timeout=self._bot.rand_float())

            return True

        return False

    def vip_mode(self):
        """
        Check if the room is in vip mode.

        :return: True if in vip mode is enabled.
        :rtype: bool
        """
        log.debug('checking vip mode, enabled=%s' % self._conf.VIP_MODE)
        if self._conf.VIP_MODE:

            if self._conf.USE_KICK_AS_AUTOBAN:
                self._bot.send_kick_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Kicked: (vip mode enabled)',
                                        timeout=self._bot.rand_float())

            else:
                self._bot.send_ban_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Banned: (vip mode enabled)',
                                        timeout=self._bot.rand_float())

            return True

        return False

    def nick(self):
        """
        Check a users nick against the nick bans.

        :return: True if the user was banned.
        :rtype: bool
        """
        log.debug('checking nick for %s' % self._user)

        if self._nick():

            if self._conf.USE_KICK_AS_AUTOBAN:
                self._bot.send_kick_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Kicked: (nick not allowed)',
                                        timeout=self._bot.rand_float())
            else:
                self._bot.send_ban_msg(self._user.handle)

                if self._conf.NOTIFY_ON_BAN:
                    self._bot.responder('Auto-Banned: (nick not allowed)',
                                        timeout=self._bot.rand_float())
            return True

        return False

    def _nick(self):

        for nick in self._conf.NICK_BANS:

            if nick.startswith('*'):
                _ = nick.lstrip('*')
                if _ in self._user.nick:
                    return True

            elif nick == self._user.nick:
                return True

        return False

    def message(self):
        """
        Check message for string ban.
        """
        if not self._user.is_mod:

            if self._timed():
                self._bot.send_ban_msg(self._user.handle)

            else:

                if self._message():

                    if self._conf.USE_KICK_AS_AUTOBAN:
                        self._bot.send_kick_msg(self._user.handle)

                        if self._conf.NOTIFY_ON_BAN:
                            self._bot.responder('Auto-Kicked',
                                                timeout=self._bot.rand_float())
                    else:
                        self._bot.send_ban_msg(self._user.handle)

                        if self._conf.NOTIFY_ON_BAN:
                            self._bot.responder('Auto-Banned',
                                                timeout=self._bot.rand_float())

    def _message(self):

        if self._msg is not None:
            log.debug('checking message %s' % self._msg.text)

            chat_words = self._msg.text.split(' ')

            for bad in self._conf.STRING_BANS:

                if bad.startswith('*'):
                    _ = bad.replace('*', '')
                    if _ in repr(self._msg.text):

                        return True

                elif bad in chat_words:

                    return True

            return False

        return False

    def _timed(self):

        if not self._conf.TRY_TIME_BASED_CHECKS:
            return False

        now = datetime.datetime.now()

        ts = now - self._user.join_time

        if ts.seconds == 0 and ts.microseconds < 400000:
            return True

        elif len(self._user.messages) > 1:
            prev = self._user.messages[-2]
            last = self._user.messages[-1]

            msg_time = last.timestamp - prev.timestamp
            if msg_time.seconds == 0 and msg_time.microseconds < 400000:
                return True

        return False
