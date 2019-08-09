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
import time
import random

from page import Privacy
from apis import Youtube, other
from util import Timer, ThreadPool, Color, file_handler, PlayList
from handlers import JoinHandler, NickHandler, \
    MessageHandler, CommandHandler
from users import User
import tinychat


log = logging.getLogger(__name__)

CONF = tinychat.CONF
other.WEATHER_API_KEY = CONF.WEATHER_KEY


class NortBot(tinychat.Client):

    privacy = None
    search_list = []
    bl_search_list = []
    is_search_list_yt_playlist = False
    playlist = PlayList()
    timer = Timer()
    pool = ThreadPool(CONF.THREAD_POOL)
    live_count = None
    _init_time = time.time()
    vote = None

    @property
    def config_path(self):
        """
        Returns the path to the rooms configuration directory.

        :return: The config path for a room.
        :rtype: str
        """
        return CONF.CONFIG_PATH + self.room + '/'

    @property
    def up_time(self):
        """
        Returns the time since init.

        :return: The time since init.
        :rtype: int
        """
        return int(time.time() - self._init_time)

    # Event Overrides.
    def on_joined(self, data):  # P
        """
        Received when the client have joined the room successfully.

        :param data: This contains info about the client,
        such as user role and so on.
        :type data: dict
        """
        log.info('client info: %s' % data)
        client = self.users.add(data.get('self'), is_client=True)
        if client.account is not None:
            self.console.write('Client joined `%s` as: %s:%s:%s' %
                               (self.room, client.nick, client.handle,
                                client.account), Color.B_GREEN)
        else:
            self.console.write('Client joined `%s` as: %s:%s' %
                               (self.room, client.nick, client.handle),
                               Color.B_GREEN)

        self.on_room_info(data.get('room'))
        self.pool.add_task(self._options)

    def on_userlist(self, user_list):  # P
        """
        Received upon joining a room.

        :param user_list: All users in the room.
        :type user_list: list
        """
        for user in user_list:
            if user.is_owner:
                self.console.write('Joins room owner: %s:%s:%s' %
                                   (user.nick, user.handle, user.account),
                                   Color.B_BLUE)
            elif user.is_mod:
                self.console.write('Joins room moderator: %s:%s:%s' %
                                   (user.nick, user.handle, user.account),
                                   Color.B_RED)
            elif user.account:
                if user.account in CONF.APPROVED:
                    self.users.mark_as_approved(user.handle)
                else:
                    self.console.write('Joins: %s:%s:%s' %
                                       (user.nick, user.handle, user.account),
                                       Color.B_GREEN)
            else:
                self.console.write('Joins: %s:%s' %
                                   (user.nick, user.handle), Color.B_YELLOW)

    def on_join(self, user):  # P
        """
        Received when a user joins the room.

        :param user: The User object of the user joining.
        :type user: users.User
        """
        jh = JoinHandler(self, user, CONF)
        jh.console()
        if self.users.client.is_mod:
            self.pool.add_task(jh.handle)

    def on_nick(self, user):  # P
        """
        Received when a user changes nick name.

        :param user: The user changing nick as User object.
        :type user: Users.User
        """
        nh = NickHandler(self, user, CONF)
        nh.console()
        if self.users.client.is_mod:
            self.pool.add_task(nh.handle)

    def on_msg(self, user, msg):  # P
        """
        Received when a message is sent to the room.

        :param user: The user sending a message as User object.
        :type user: Users.User
        :param msg: The message as TextMessage object.
        :type msg: TextMessage
        """
        if user.handle != self.users.client.handle:
            mh = MessageHandler(self, user, CONF, msg)
            # write message to console
            mh.console()

            if self.users.client.is_mod:
                # check message for ban string
                self.pool.add_task(mh.handle)

                # initialize the command handler
                ch = CommandHandler(self, user, msg, CONF, self.pool)
                # handle command
                ch.handle()

    def on_pvtmsg(self, user, msg):  # P
        """
        Received when a user sends the client a private message.

        :param user: The user sending a private message as User object.
        :type user: Users.User
        :param msg: The text message as TextMessage object.
        :type msg: TextMessage
        """
        if user.handle != self.users.client.handle:
            mh = MessageHandler(self, user, CONF, msg)
            # write message to console
            mh.console()

            if self.users.client.is_mod:
                # check private message for ban string
                self.pool.add_task(mh.handle)

                # initialize the command handler
                ch = CommandHandler(self, user, msg, CONF, self.pool)
                # handle command
                ch.handle()

    def on_pending_moderation(self, user):  # P
        """
        Received when a user is waiting in the green room.

        :param user: The user waiting in the green room as User object.
        :type user: Users.User
        """
        if user.account is not None and user.account in CONF.APPROVED:
            self.send_cam_approve_msg(user.handle)
            self.console.write('%s:%s:%s was auto approved for broadcast' %
                               (user.nick, user.handle, user.account), Color.B_CYAN)
        else:
            self.console.write('%s:%s is waiting for broadcast approval.' %
                               (user.nick, user.handle), Color.B_YELLOW)

    def on_publish(self, user):  # P
        """
        Received when a user starts broadcasting.

        :param user: The user broadcasting as User object.
        :type user: Users.User
        """
        if not user.can_broadcast:
            self.send_close_user_msg(user.handle)
            self.console.write('Auto closing broadcast for: %s:%s' %
                               (user.nick, user.handle), Color.B_BLUE)
        else:
            self.console.write('%s:%s is broadcasting.' %
                               (user.nick, user.handle), Color.BLUE)

    def on_yut_play(self, user, youtube):  # P
        """
        Received when a youtube gets started or searched.

        :param user: The User object of the user
        starting or searching the youtube.
        :type user: Users.User
        :param youtube: The YoutubeMessage object.
        :type youtube: message.YoutubeMessage
        """
        track = Youtube.id_details(youtube.video_id)

        if user is None:
            self.playlist.start('started @ join', track)
            remaining = self.playlist.play(youtube.offset)
            self.timer.start(self.timer_event, remaining)

            self.console.write('[YOUTUBE] %s is playing.' %
                               youtube.title, Color.B_YELLOW)
        else:
            if not youtube.is_response:

                if self.playlist.has_active_track:
                    self.timer.cancel()

                if youtube.offset == 0:
                    self.playlist.start(user.nick, track)
                    self.timer.start(self.timer_event, track.time)

                    self.console.write('%s is playing %s' %
                                       (user.nick, youtube.title),
                                       Color.B_YELLOW)

                elif youtube.offset > 0:
                    remaining = self.playlist.play(youtube.offset)
                    self.timer.start(self.timer_event, remaining)

                    self.console.write('%s searched %s to %s' %
                                       (user.nick, youtube.title,
                                        youtube.offset), Color.B_YELLOW)

    def on_yut_pause(self, user, youtube):  # P
        """
        Received when a youtube gets paused or searched while paused.

        :param user: The User object of the user pausing the video.
        :type user: Users.User
        :param youtube: The YoutubeMessage object.
        :type youtube: message.YoutubeMessage
        """
        if user is None:
            track = Youtube.id_details(youtube.video_id)
            self.playlist.start('paused @ join', track)
            self.playlist.pause(youtube.offset)

            self.console.write('[YOUTUBE] %s is paused.' % youtube.title)

        else:

            if not youtube.is_response:

                if self.playlist.has_active_track:
                    self.timer.cancel()
                self.playlist.pause()

                self.console.write('%s paused %s at %s' %
                                   (user.nick, youtube.title,
                                    youtube.offset), Color.B_YELLOW)

    # CONFIRMED. If a video is stopped(by a mod)
    # and there is remaining tracks in the playlist, then
    # the next video in the playlist would start playing,
    # once the time of the stopped video was done. This is
    # is happening because the timer does not get cancelled.

    # maybe add a check to see if the youtube was stopped before
    # the video time was reached (offset v.s video time)

    # Timed Event.
    def timer_event(self):
        """
        This gets called when the timer has reached the time.
        """
        if len(self.playlist.track_list) > 0:
            if self.playlist.is_last_track:
                if self.connected:
                    self.send_chat_msg('Resetting playlist.')
                self.playlist.clear()
            else:
                track = self.playlist.next_track
                if track is not None and self.connected:
                    self.send_yut_play(track.id, track.time, track.title)

                self.timer.start(self.timer_event, track.time)

    # Helpers.
    @staticmethod
    def rand_float(start=0.5, end=CONF.MAX_NOTIFY_DELAY, decimals=2):
        """
        Creates a random float between start and end with
        up to N decimals.

        :param start: The lowest float.
        :type start: int | float
        :param end: The max float.
        :type end: int | float
        :param decimals: The amount of decimals.
        :type decimals: int
        :return: A random float between start and end.
        :rtype: float
        """
        return round(random.uniform(start, end), decimals)

    def responder(self, msg, msg_type=1, user=None, timeout=0.0):
        """
        A wrapper around the send_chat_msg and
        send_private_msg.

        It is important to understand, that if the
        timeout is to be used, then the parent
        caller *must* be running in a thread.

        :param msg: The message to send.
        :type msg: str
        :param msg_type: The type of the message,
        1 = public chat message, 2 = private chat message.
        :param user: If the user is a User instance,
        and the msg type is 2, then the message
        will be sent as private message.
        :type user: User
        :param timeout: The time to sleep before the message
        will be sent.
        :type timeout: int | float
        """
        if timeout > 0.0:
            time.sleep(timeout)

        if msg_type == 2 and isinstance(user, User):
            self.send_private_msg(user.handle, msg)
        else:
            self.send_chat_msg(msg)

    def get_list(self, approved=False, nicks=False,
                 accounts=False, strings=False):
        """
        Read bot specific files to memory.

        :param approved: Read the approved accounts file.
        :type approved: bool
        :param nicks: Read the nick bans file.
        :type nicks: bool
        :param accounts: Read the account bans file.
        :type accounts: bool
        :param strings: Read the string bans file.
        :type strings: bool
        """
        log.debug('reading file: approved=%s, nicks=%s, '
                  'accounts=%s, strings=%s' %
                  (approved, nicks, accounts, strings))

        if approved:
            CONF.APPROVED = file_handler.reader(
                self.config_path, CONF.APPROVED_FILE_NAME)
        if nicks:
            CONF.NICK_BANS = file_handler.reader(
                self.config_path, CONF.NICK_BANS_FILE_NAME)
        if accounts:
            CONF.ACCOUNT_BANS = file_handler.reader(
                self.config_path, CONF.ACCOUNT_BANS_FILE_NAME)
        if strings:
            CONF.STRING_BANS = file_handler.reader(
                self.config_path, CONF.STRING_BANS_FILE_NAME)

    @staticmethod
    def format_time(time_stamp, is_milli=False):
        """
        Converts a time stamp as seconds or milliseconds
        to (day(s)) hours minutes seconds.

        :param time_stamp: Seconds or milliseconds to convert.
        :param is_milli: The time stamp to format is in milliseconds.
        :return: A string in the format (days) hh:mm:ss
        :rtype: str
        """
        if is_milli:
            m, s = divmod(time_stamp / 1000, 60)
        else:
            m, s = divmod(time_stamp, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        if d == 0 and h == 0:
            human_time = '%02d:%02d' % (m, s)
        elif d == 0:
            human_time = '%d:%02d:%02d' % (h, m, s)
        else:
            human_time = '%d Day(s) %d:%02d:%02d' % (d, h, m, s)

        return human_time

    # Private Internals.
    def _options(self):
        if self.users.client.is_owner:
            self._privacy_settings()

        if self.users.client.is_mod:
            self.send_banlist()
            self.get_list(approved=True, nicks=True,
                          accounts=True, strings=True)

    def _privacy_settings(self):
        self.privacy = Privacy(self.proxy)
        self.privacy.parse_settings()
