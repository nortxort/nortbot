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

import json
import logging

import websocket
import config
from users import Users
from page import Account
from apis import TinychatApi
from room import RoomState
from _process_event import ProcessEvent
from util import string_util, Console, Color, captcha, thread_task


log = logging.getLogger(__name__)

# since the config is loaded at import,
# we add a reference here so we can
# access it through tinychat
CONF = config


class ClientBaseError(Exception):
    pass


class InvalidRoomNameError(ClientBaseError):
    pass


class InvalidNickNameError(ClientBaseError):
    pass


class InvalidAccountNameError(ClientBaseError):
    pass


class Client:
    def __init__(self, room, nick=None, **kwargs):
        self.room = room
        self.nick = nick
        self.account = kwargs.get('account')
        self.password = kwargs.get('password')
        self.room_pass = kwargs.get('room_pass')

        self.proxy = kwargs.get('proxy', None)

        self.users = Users()
        self.state = RoomState()
        self.console = Console(self.room,
                               log_path=config.CONFIG_PATH,
                               chat_logging=config.CHAT_LOGGING,
                               use_colors=config.CONSOLE_COLORS)
        self._connect_args = None
        self._ws = None
        self._is_connected = False
        self._req = 1

        captcha.MAX_TRIES = kwargs.get('captcha_tries', 11)
        captcha.CAPTCHA_TIMEOUT = kwargs.get('captcha_timeout', 5)

        if self.nick is None or self.nick == '':
            self.nick = string_util.create_random_string(3, 20)

    @property
    def connected(self):
        """
        True if connected, else False.
        """
        return self._is_connected

    @property
    def page_url(self):
        """
        Return the url of the room.
        """
        return 'https://tinychat.com/room/%s' % self.room

    def login(self):
        """
        Login to tinychat.

        :return: True if logged in, else False
        :rtype: bool
        """
        if self.account is not None and self.password is not None:

            if not string_util.is_valid_string(self.account):
                raise InvalidAccountNameError('account name may only contain letter(a-z) and numbers(0-9)')
            else:

                account = Account(self.account, self.password, self.proxy)
                if not account.is_logged_in():

                    if account.login():
                        self.console.write('Logged in as `%s`' % self.account,
                                           Color.B_GREEN)
                    else:
                        self.console.write('Failed to login as `%s`' % self.account,
                                           Color.B_RED)

                return account.is_logged_in()

        return False

    def connect(self):
        """
        Connect to the websocket server.
        """
        if not string_util.is_valid_string(self.room):
            raise InvalidRoomNameError(
                'room name may only contain letters(a-z) and numbers(0-9).')

        else:
            tc_header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-WebSocket-Protocol': 'tc',
                'Sec-WebSocket-Extensions': 'permessage-deflate'
            }

            websocket.enableTrace(config.DEBUG_MODE)

            self._connect_args = TinychatApi.connect_token(self.room)
            if self._connect_args is not None:

                self._ws = websocket.WebSocketApp(
                    self._connect_args['endpoint'],
                    header=tc_header,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_pong=self.on_pong
                )

                self._ws.run_forever(
                    origin='https://tinychat.com',
                    ping_interval=20,
                    ping_timeout=5
                )
            else:
                log.info('missing connect args %s' % self._connect_args)

    def disconnect(self):
        """
        Disconnect from the websocket server
        """
        log.info('disconnecting from server')
        if self._ws is not None:
            self._ws.close(timeout=0)

        self._req = 1
        self._ws = None
        self.users.clear()
        self.users.clear_banlist()

    def reconnect(self):
        """
        Reconnect to the server.
        """
        log.info('reconnecting')
        if self.connected:  # this check might not be needed anymore
            self.disconnect()

        # maybe add a timeout here
        self.login()
        self.connect()

    # Event Dispatcher.
    def dispatch(self, event, event_data):
        """
        Dispatch an event to a handler.

        :param event: The event to dispatch.
        :type event: str
        :param event_data: The event data.
        :type event_data: dict
        """
        log.debug('dispatching event: %s' % event)
        method = 'on_%s' % event

        if hasattr(self, method):
            ProcessEvent(self, event, method, event_data).process()
        else:
            e = 'no event handler for `%s`' % event
            log.info(e)
            if config.DEBUG_MODE:
                self.console.write(e, Color.B_RED)

    # Method Caller.
    def run_method(self, method, *args, **kwargs):
        """
        Call a method.

        :param method: The name of the method to run.
        :type method: str
        """
        func = getattr(self, method, None)
        if func is not None:
            func(*args, **kwargs)

    # Error Handler.
    def error(self, event, error):
        """
        Client event error handler.

        :param event: The event of the error.
        :type event: str
        :param error: Error description.
        :type error: str
        """
        self.console.write('[ERROR] `%s` %s' % (event, error),
                           Color.B_RED)

    # Websocket Events.
    def on_pong(self, data):
        """
        Called in a response to the PING we send.

        NOTE: For some reason the data
        param is always empty. Apparently
        it should be frame.data, what ever
        that is (websocket._app.py line 278)

        :param data: I assume this should be PONG data.
        :type data: str
        """
        _ = 'websocket pong data %s' % data
        if config.DEBUG_MODE:
            self.console.write(_, Color.B_GREEN)
        log.info(_)

    def on_error(self, error):
        """
        Called if a websocket error occurs.
        """
        if isinstance(error, websocket.WebSocketTimeoutException):
            self.console.write('%s, reconnecting..' % error, Color.B_RED)
            self.reconnect()
        else:
            self.error(type(error), error)

    def on_close(self):
        """
        Called when/if the websocket connection gets closed.
        """
        self._is_connected = False
        self.console.write('[CLOSED] the connection was closed.',
                           Color.B_RED)

    def on_open(self):
        """
        Called when the websocket handshake has been established.
        """
        log.info('websocket connection connected.')
        self._is_connected = True
        self._join()

    def on_message(self, message):
        """
        Called when we receive a message from the websocket endpoint.

        :param message: The websocket message.
        :type message: str
        """
        if message:
            json_data = json.loads(message)

            log.debug('[RAW DATA] %s' % json_data)
            event = json_data['tc']

            if event == 'ping':
                self.on_ping()
            else:
                self.dispatch(event, json_data)

    # Application Events.
    def on_ping(self):
        """
        Received on application ping.
        """
        self.send_pong()

    def on_closed(self, data):
        """
        Received when ever the connection gets closed
        by the server for what ever reason.

        :param data: The close data.
        :type data: dict
        """
        code = data.get('error')
        if code == 0:
            self.console.write('There is no internet connection.',
                               Color.B_RED)
        elif code == 1:
            self.console.write('Oops, chatroom has no free slots for users.',
                               Color.B_RED)
        elif code == 2:
            self.console.write('Chatroom has been closed by administrator.',
                               Color.B_RED)
        elif code == 3:
            self.console.write('Closed with code %s' % code,
                               Color.B_RED)
        elif code == 4:
            self.console.write('You have been banned from the room.',
                               Color.B_RED)
        elif code == 5:
            self.console.write('Reconnect code? %s' % code,
                               Color.B_RED)
            self.reconnect()
        elif code == 6:
            self.console.write('Double account sign in.',
                               Color.B_RED)
        elif code == 7:
            self.console.write('An error occurred while connecting to the server.',
                               Color.B_RED)
        elif code == 8:
            # timeout error. usually when not entering
            # password or captcha within ~60 seconds.
            self.console.write('Timeout error %s' % code, Color.B_RED)
        elif code in [9, 10, 11]:
            # not sure why these occur
            self.console.write('Something went wrong, code %s' % code,
                               Color.B_RED)
        elif code == 12:
            self.console.write('You have been kicked by a moderator.',
                               Color.B_RED)
            self.reconnect()
        elif code == 22:
            self.console.write('You must be at least 18 years old and '
                               'signed in to a verified Tinychat account to join this room',
                               Color.B_RED)
        else:
            self.console.write('Connection was closed, code: %s' % code,
                               Color.B_RED)
        # is connected is False in any of these cases
        self._is_connected = False

    def on_joined(self, data):
        """
        Received when the client have joined the room successfully.

        :param data: This contains info about the client,
        such as user role and so on.
        :type data: dict
        """
        log.info('client info: %s' % data)
        client = self.users.add(data.get('self'), is_client=True)
        self.console.write('Client joined the room: %s:%s' %
                           (client.nick, client.handle), Color.B_GREEN)

        if client.is_mod:
            self.send_banlist()

        self.on_room_info(data.get('room'))

    def on_room_info(self, room_info):
        """
        Received when the client have joined the room successfully.

        This information will only show in the console
        if debug is enabled.

        :param room_info: This contains information about the room
        such as about, profile image and so on.
        :type room_info: dict
        """
        self.state.update(**room_info)
        if config.DEBUG_MODE:
            self.console.write('<Room Information>')
            self.console.write(self.state.formatted(), ts=False)

    def on_room_settings(self, room_settings):
        """
        Received when a change has been made to
        the room settings(privacy page).

        This information will only show in the console
        if debug is enabled.

        :param room_settings: The room settings.
        :type room_settings: dict
        """
        self.state.update(**room_settings)
        self.console.write('<Room State Changed>')
        if config.DEBUG_MODE:
            self.console.write(self.state.formatted(), ts=False)

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
                self.console.write('Joins: %s:%s:%s' %
                                   (user.nick, user.handle, user.account),
                                   Color.B_GREEN)
            else:
                self.console.write('Joins: %s:%s' %
                                   (user.nick, user.handle), Color.B_YELLOW)

    def on_join(self, user):  # P
        """
        Received when a user joins the room.

        :param user: The user joining as User object.
        :type user: Users.User
        """
        if user.account:
            tc_info = TinychatApi.user_info(user.account)
            if tc_info is not None:
                self.users.add_tc_info(user.handle, tc_info)

            if user.is_owner:
                self.console.write('Owner joined: %s:%s:%s' %
                                   (user.nick, user.handle, user.account),
                                   Color.B_BLUE)
            elif user.is_mod:
                self.console.write('Moderator joined: %s:%s:%s' %
                                   (user.nick, user.handle, user.account),
                                   Color.B_RED)
            elif user.account:
                self.console.write('User joined: %s:%s:%s' %
                                   (user.nick, user.handle, user.account),
                                   Color.B_GREEN)
        else:
            self.console.write('Guest joined: %s:%s' %
                               (user.nick, user.handle), Color.B_YELLOW)

    def on_nick(self, user):   # P
        """
        Received when a user changes nick name.

        :param user: The user changing nick as User object.
        :type user: Users.User
        """
        old_nick = user.old_nicks[-2]
        self.console.write('%s changed nick to %s:%s' %
                           (old_nick, user.nick, user.handle),
                           Color.B_CYAN)

    def on_quit(self, user):  # P
        """
        Received when a user leaves the room.

        :param user: The user leaving as User object.
        :type user: Users.User
        """
        if user is not None:
            # user can be None if user is broadcasting, and then leaves?
            self.console.write('%s:%s left the room.' %
                               (user.nick, user.handle),
                               Color.B_CYAN)

    def on_ban(self, banned):  # P
        """
        Received when the client bans a user.

        TODO: Test this

        :param banned: The user who was banned.
        :type banned: Users.BannedUser
        """
        self.console.write('%s was banned.' % banned.nick,
                           Color.B_RED)

    def on_unban(self, unbanned):  # P
        """
        Received when the client un-bans a user.

        TODO: Test this

        :param unbanned: The banned user who was unbanned.
        :type unbanned: Users.BannedUser
        """
        self.console.write('%s was unbanned.' % unbanned.nick,
                           Color.B_MAGENTA)

    def on_banlist(self, banlist):  # P
        """
        Received when a request for the ban list has been made.

        :param banlist: A list of BannedUser objects.
        :type banlist: list
        """
        for banned in banlist:
            if banned.account is not None:
                self.console.write('Nick: %s, Account: %s, Banned By: %s' %
                                   (banned.nick, banned.account,
                                    banned.banned_by), Color.B_RED)
            else:
                self.console.write('Nick: %s, Banned By: %s' %
                                   (banned.nick, banned.banned_by),
                                   Color.B_RED)

    def on_msg(self, user, msg):  # P
        """
        Received when a message is sent to the room.

        :param user: The user sending a message as User object.
        :type user: Users.User
        :param msg: The text message as TextMessage object.
        :type msg: TextMessage
        """
        self.console.write('%s: %s ' % (user.nick, msg.text),
                           Color.B_GREEN)

    def on_pvtmsg(self, user, msg):  # P
        """
        Received when a user sends the client a private message.

        :param user: The user sending a private message as User object.
        :type user: Users.User
        :param msg: The text message as TextMessage object.
        :type msg: TextMessage
        """
        self.console.write('[PM] %s: %s' % (user.nick, msg.text),
                           Color.WHITE)

    def on_publish(self, user):  # P
        """
        Received when a user starts broadcasting.

        :param user: The user broadcasting as User object.
        :type user: Users.User
        """
        self.console.write('%s:%s is broadcasting.' %
                           (user.nick, user.handle), Color.BLUE)

    def on_unpublish(self, user):  # P
        """
        Received when a user stops broadcasting.

        :param user: The user who stops broadcasting as User object.
        :type user: Users.User
        """
        self.console.write('%s:%s stopped broadcasting.' %
                           (user.nick, user.handle), Color.BLUE)

    def on_sysmsg(self, msg):
        """
        System messages sent from the server to all clients (users).

        These messages are special events notifications.

        :param msg: The special notifications message data.
        :type msg: dict
        """
        text = msg.get('text')

        if 'banned' in text and self.users.client.is_mod:
            self.users.clear_banlist()
            self.send_banlist()
        elif 'green room enabled' in text:
            self.state.set_greenroom(True)
        elif 'green room disabled' in text:
            self.state.set_greenroom(False)

        self.console.write('[SYSTEM]: %s' % text, Color.WHITE)

    def on_password(self, req_id):  # P
        """
        Received when a room is password protected.

        An on_closed event with code 8 will be called
        if a password has not been provided within
        ~60 seconds

        3 password attempts can be tried
        before a reconnect is required.

        TODO: If the room_pass is correct, add it to RoomState? How?
        """
        self.console.write('Password protected room (%s)' % req_id,
                           Color.B_RED)

        if self.room_pass is not None and req_id == 1:
            self.console.write('Sending room password: %s' % self.room_pass,
                               Color.GREEN)

        elif self.room_pass is not None and req_id > 1:
            # TODO: Maybe add user input..
            self.console.write('The room password provided is '
                               'incorrect, closing.', Color.B_RED)
            self.disconnect()

    def on_pending_moderation(self, user):  # P
        """
        Received when a user is waiting in the green room.

        :param user: The user waiting in the green room as User object.
        :type user: Users.User
        """
        self.console.write('%s:%s is waiting for broadcast approval.' %
                           (user.nick, user.handle), Color.B_YELLOW)

    def on_stream_moder_allow(self, allowed, allowed_by):  # P
        """
        Received when a user has been
        allowed to broadcast in a green room.

        :param allowed: The user that was allowed to broadcast.
        :type allowed: Users.User
        :param allowed_by: The user allowing the broadcast.
        :type allowed_by: Users.User
        """
        if allowed_by.handle == self.users.client.handle:
            self.console.write('The bot allowed %s:%s to broadcast.' %
                               (allowed.nick, allowed.handle), Color.B_GREEN)
        else:
            self.console.write('%s:%s allowed %s:%s to broadcast.' %
                               (allowed_by.nick, allowed_by.handle,
                                allowed.nick, allowed.handle),
                               Color.B_YELLOW)

    def on_stream_moder_close(self, closed):  # P
        """
        Received when a user has their broadcast
        closed by the client.

        :param closed: The user that was closed.
        :type closed: Users.User
        """
        self.console.write('%s:%s was closed.' %
                           (closed.nick, closed.handle), Color.B_YELLOW)

    def on_captcha(self, site_key):  # P
        """
        Received when a room has captcha enabled.

        :param site_key: The captcha site key.
        :type site_key: str
        """
        if config.ANTI_CAPTCHA_KEY is not None:
            self.console.write('Starting captcha solving service, please wait...',
                               Color.B_GREEN)
            thread_task(self._captcha_service, site_key)
        else:
            self.console.write('Captcha %s' % site_key, Color.B_RED, ts=False)

            self.disconnect()

    def _captcha_service(self, site_key):
        try:
            ac = captcha.AntiCaptcha(self.page_url, config.ANTI_CAPTCHA_KEY)
            response = ac.solver(site_key)

        except (captcha.NoFundsError, captcha.MaxTriesError) as e:
            self.console.write(e)
            self.disconnect()

        except captcha.AntiCaptchaApiError as ace:
            self.console.write(ace.description)
            self.disconnect()

        else:
            if response.token is not None:
                self.console.write('Captcha solved in %s seconds with '
                                   '%s tries and a cost of %s$' %
                                   (response.solve_time, response.tries,
                                    response.cost), Color.B_GREEN)
                self.send_captcha(response.token)

    # Media Events.
    def on_yut_playlist(self, playlist_data):
        """
        Received when a request for the playlist has been made.

        The playlist is as, one would see if being a moderator
        and using a web browser.

        :param playlist_data: The data of the items in the playlist.
        :type playlist_data: dict
        """
        pass

    def on_yut_play(self, user, youtube):  # P
        """
        Received when a youtube gets started or searched.

        :param user: The User object of the user
        starting or searching the youtube.
        :type user: Users.User
        :param youtube: The YoutubeMessage object.
        :type youtube: YoutubeMessage
        """
        if user is None:
            self.console.write('[YOUTUBE] %s is playing.' %
                               youtube.title, Color.B_YELLOW)
        else:
            if not youtube.is_response:
                if youtube.offset == 0:
                    self.console.write('%s is playing %s' %
                                       (user.nick, youtube.title),
                                       Color.B_YELLOW)

                elif youtube.offset > 0:
                    self.console.write('%s searched %s to %s' %
                                       (user.nick, youtube.title,
                                        youtube.offset), Color.B_YELLOW)

    def on_yut_pause(self, user, youtube):  # P
        """
        Received when a youtube gets paused or searched while paused.

        :param user: The User object of the user pausing the video.
        :type user: Users.User
        :param youtube: The YoutubeMessage object.
        :type youtube: YoutubeMessage
        """
        if not youtube.is_response:
            self.console.write('%s paused %s at %s' %
                               (user.nick, youtube.title,
                                youtube.offset), Color.B_YELLOW)

    def on_yut_stop(self, youtube):  # P
        """
        Received when a youtube is stopped.

        :param youtube: The YoutubeMessage object.
        :type youtube: YoutubeMessage
        """
        self.console.write('%s was stopped at %s (%s)' %
                           (youtube.title, youtube.offset,
                            youtube.duration), Color.B_YELLOW)

    # Message Construction.
    def _join(self):
        """
        The initial connect message to the room.

        The client sends this after the websocket handshake has been established.
        """
        pat = '^[a-zA-Z0-9_]*$'
        if not string_util.is_valid_string(self.nick, pattern=pat):
            raise InvalidNickNameError('nick name may only contain a-zA-Z0-9_')

        else:

            rtc_version = TinychatApi.rtc_version(self.room)
            if rtc_version is None:
                rtc_version = config.FALLBACK_RTC_VERSION
                log.debug(
                    'failed to parse rtc version, using fallback: %s' % rtc_version)

            payload = {
                'tc': 'join',
                'req': self._req,
                'useragent': 'tinychat-client-webrtc-undefined_win32-' + rtc_version,
                'token': self._connect_args['token'],
                'room': self.room,
                'nick': self.nick
            }
            self.send(payload)

    def send_pong(self):
        """
        Send a response to a ping.
        """
        payload = {
            'tc': 'pong',
            'req': self._req
        }
        self.send(payload)

    def set_nick(self):
        """
        Send a nick message.
        """
        payload = {
            'tc': 'nick',
            'req': self._req,
            'nick': self.nick
        }
        self.send(payload)

    def send_chat_msg(self, msg):
        """
        Send a chat message to the room.

        :param msg: The message to send.
        :type msg: str
        """
        payload = {
            'tc': 'msg',
            'req': self._req,
            'text': msg
        }
        self.send(payload)

    def send_private_msg(self, handle, msg):
        """
        Send a private message to a user.

        :param handle: The handle of the user to send the message to.
        :type handle: int
        :param msg: The private message to send.
        :type msg: str
        """
        payload = {
            'tc': 'pvtmsg',
            'req': self._req,
            'text': msg,
            'handle': handle
        }
        self.send(payload)

    def send_kick_msg(self, handle):
        """
        Send a kick message to kick a user out of the room.

        :param handle: The handle of the user to kick.
        :type handle: int
        """
        payload = {
            'tc': 'kick',
            'req': self._req,
            'handle': handle
        }
        self.send(payload)

    def send_ban_msg(self, handle):
        """
        Send a ban message to ban a user from the room.

        :param handle: The handle of the user to ban.
        :type handle: int
        """
        payload = {
            'tc': 'ban',
            'req': self._req,
            'handle': handle
        }
        self.send(payload)

    def send_unban_msg(self, ban_id):
        """
        Send a un-ban message to un-ban a banned user.

        :param ban_id: The ban ID of the user to un-ban.
        :type ban_id: int
        """
        payload = {
            'tc': 'unban',
            'req': self._req,
            'id': ban_id
        }
        self.send(payload)

    def send_banlist(self):
        """
        Send a banlist request message.
        """
        payload = {
            'tc': 'banlist',
            'req': self._req
        }
        self.send(payload)

    def send_room_password_msg(self, password):
        """
        Send a room password message.

        :param password: The room password.
        :type password: str
        """
        payload = {
            'tc': 'password',
            'req': self._req,
            'password': password
        }
        self.send(payload)

    def send_cam_approve_msg(self, handle):
        """
        Allow a user to broadcast in green room enabled room.

        :param handle: The handle of the user.
        :type handle: int
        """
        payload = {
            'tc': 'stream_moder_allow',
            'req': self._req,
            'handle': handle
        }
        self.send(payload)

    def send_close_user_msg(self, handle):
        """
        Close a users broadcast.

        :param handle: The handle of the user.
        :type handle: int
        """
        payload = {
            'tc': 'stream_moder_close',
            'req': self._req,
            'handle': handle
        }
        self.send(payload)

    def send_captcha(self, token):
        """
        Send the captcha token.

        :param token: The captcha response token.
        :type token: str
        """
        payload = {
            'tc': 'captcha',
            'req': self._req,
            'token': token
        }
        self.send(payload)

    # Media.
    def send_yut_playlist(self):
        """
        Send a youtube playlist request.
        """
        payload = {
            'tc': 'yut_playlist',
            'req': self._req
        }
        self.send(payload)

    def send_yut_playlist_add(self, video_id, duration, title, image):
        """
        Add a youtube to the web browser playlist.

        I haven't explored this yet.

        :param video_id: the ID of the youtube video.
        :type video_id: str
        :param duration: The duration of the youtube video (in seconds).
        :type duration: int
        :param title: The title of the youtube video.
        :type title: str
        :param image: The thumbnail image url of the video.
        :type image: str
        """
        payload = {
            'tc': 'yut_playlist_add',
            'req': self._req,
            'item': {
                'id': video_id,
                'duration': duration,
                'title': title,
                'image': image
            }
        }
        self.send(payload)

    def send_yut_playlist_remove(self, video_id, duration, title, image):
        """
        Remove a playlist item from the web browser based playlist.

        I haven't explored this yet.

        :param video_id: The ID of the youtube video to remove.
        :type video_id: str
        :param duration: The duration of the youtube video to remove.
        :type duration: int | float
        :param title: The title of the youtube video to remove.
        :type title: str
        :param image: The thumbnail image url of the youtube video to remove.
        :type image: str
        """
        payload = {
            'tc': 'yut_playlist_remove',
            'req': self._req,
            'item': {
                'id': video_id,
                'duration': duration,
                'title': title,
                'image': image
            }
        }
        self.send(payload)

    def send_yut_playlist_mode(self, random_=False, repeat=False):
        """
        Set the mode of the web browser based playlist.

        I haven't explored this yet.

        :param random_: Setting this to True will make videos play at random i assume.
        :type random_: bool
        :param repeat: Setting this to True will make the playlist repeat itself i assume.
        :type repeat: bool
        """
        payload = {
            'tc': 'yut_playlist_mode',
            'req': self._req,
            'mode': {
                'random': random_,
                'repeat': repeat
            }
        }
        self.send(payload)

    def send_yut_play(self, video_id, duration, title, offset=0):
        """
        Start or search a youtube video.

        :param video_id: The ID of the youtube video to start or search.
        :type video_id: str
        :param duration: The duration of the video in seconds.
        :type duration: int | float
        :param title: The title of the youtube.
        :type title: str
        :param offset: The offset seconds to start the video at in the case of doing a search.
        :type offset: int | float
        """
        payload = {
            'tc': 'yut_play',
            'req': self._req,
            'item': {
                'id': video_id,
                'duration': duration,
                'offset': offset,
                'title': title
            }
        }

        if offset != 0:
            del payload['item']['title']
            payload['item']['playlist'] = False
            payload['item']['seek'] = True

        self.send(payload)

    def send_yut_pause(self, video_id, duration, offset=0):
        """
        Pause, or search while a youtube video is paused .

        :param video_id: The ID of the youtube video to pause or search.
        :type video_id: str
        :param duration: The duration of the video in seconds.
        :type duration: int |float
        :param offset: The offset seconds to pause the video at in case of doing seach while in pause.
        :type offset: int |float
        """
        payload = {
            'tc': 'yut_pause',
            'req': self._req,
            'item': {
                'id': video_id,
                'duration': duration,
                'offset': offset
            }
        }
        self.send(payload)

    def send_yut_stop(self, video_id, duration, offset=0):
        """
        Stop a youtube video that is currently playing.

        :param video_id: The ID of the youtube to stop.
        :type video_id: str
        :param duration: The duration of the youtube video in seconds.
        :type duration: int | float
        :param offset: The offset seconds when the youtube gets stopped.
        :type offset: int |float
        """
        payload = {
            'tc': 'yut_stop',
            'req': self._req,
            'item': {
                'id': video_id,
                'duration': duration,
                'offset': offset
            }
        }
        self.send(payload)

    # Message Sender Wrap.
    def send(self, payload):
        """
        Message sender wrapper used by all methods that sends.

        :param payload: The object to send.
        This should be an object that can be serialized to json.
        :type payload: dict | object
        """
        if self.connected:
            _payload = json.dumps(payload)
            self._ws.send(_payload)
            self._req += 1
            log.debug('%s connected: %s' % (_payload, self.connected))
