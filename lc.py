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
import json

import websocket


log = logging.getLogger(__name__)


class Room:
    """
    Class representing a live count room.
    """
    def __init__(self, **data):
        self._data = data

    @property
    def name(self):
        """
        Returns a room name.

        :return: A room name.
        :rtype: str
        """
        return self._data.get('room', '')

    @property
    def users(self):
        """
        Returns room users.

        :return: Room users'
        :rtype: int
        """
        return self._data.get('users', 0)

    @property
    def broadcasters(self):
        """
        Returns room broadcasters.

        :return: Room broadcasters.
        :rtype: int
        """
        return self._data.get('broadcasters', 0)


class LiveCount:
    """
    Live count class.

    Tinychat uses this data to update
    user and broadcaster count on the directory.
    """
    def __init__(self, bot, watch=None):
        """
        Initialize the LiveCount class.

        :param bot: A instance of NortBot.
        :param watch: A room name to watch.
        :type watch: str | None
        """
        self._bot = bot
        self._watch_room = watch
        self._watch_interval = 20

        self._last_update_time = 0
        self._most_active = Room()
        self._connected = False
        self._ws = None

    @property
    def connected(self):
        """
        Returns a bool based on the connection state.

        :return: True if connected.
        :rtype: bool
        """
        return self._connected

    @property
    def most_active(self):
        """
        Returns the most active room.

        :return: The room with the most users.
        :rtype: Room
        """
        return self._most_active

    def set_watch_room(self, room_name):
        """
        Set a room name to watch live count for.

        :param room_name: The room name to watch.
        :type room_name: str
        """
        self._watch_room = room_name
        self._bot.responder('Live count watch room: %s' % room_name)

    def set_watch_interval(self, interval):
        """
        Set the watch interval time.

        :param interval: Watch interval time in seconds.
        :type interval: int
        """
        self._watch_interval = interval
        self._bot.responder('Live count watch interval: %s' % interval)

    def connect(self):
        """
        Connect to the websocket endpoint.
        """
        tc_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-WebSocket-Extensions': 'permessage-deflate'
        }

        self._ws = websocket.create_connection(
            'wss://lb-stat.tinychat.com/leaderboard',
            header=tc_header,
            origin='https://tinychat.com'
        )

        if self._ws.connected:
            self._bot.responder('Live count connected.')
            self._connected = self._ws.connected
            self._listener()
        else:
            log.debug('connection to live counter failed')

    def disconnect(self):
        """
        Disconnect from the websocket.
        """
        self._bot.responder('closing live count.')
        # if self._ws is not None and self._connected:
        #     self._ws.send_close(1001, 'GoingAway')
        self._connected = False
        self._ws = None

    def on_update(self, data):
        """
        Received when ever the live count gets updated.

        :param data: A list containing room updates.
        :type data: list
        """
        log.debug('live count items %s' % len(data))

        ts = time.time()

        for room_data in data:
            room = Room(**room_data)

            # update most active room
            if room.users > self._most_active.users:
                self._most_active = room

            # is the watch room set?
            if self._watch_room is not None:

                # if the watch room is in the updated rooms..
                if self._watch_room == room.name:

                    # only send a message if >= watch interval
                    if ts - self._last_update_time >= self._watch_interval:
                        self._last_update_time = ts
                        self._bot.responder('Watching: %s, Users: %s, Broadcasters: %s' %
                                            (room.name, room.users, room.broadcasters))

    def _listener(self):
        while self.connected:
            data = self._ws.next()
            json_data = json.loads(data)

            event = json_data['ev']

            if event == 'update':
                self.on_update(json_data['data'])

            else:
                log.warning('unknown event: %s' % event)
