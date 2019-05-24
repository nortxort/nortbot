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


class TextMessage:
    """
    Class representing a received text message.

    A text message can be a public message(msg_type=1)
    or a private message(msg_type=2).
    """

    def __init__(self, event_data):
        """
        Initialize the class.

        :param event_data: The event data. This also contain
        the actual event itself.
        :type event_data: dict
        """
        self._text = event_data.get('text')
        self._event = event_data.get('tc')
        self._msg_type = 1
        self._ts = datetime.now()

        if self._event == 'pvtmsg':
            self._msg_type = 2

    @property
    def type(self):
        """
        The type of the message.

        :return: The msg type of the message.
        :rtype: int
        """
        return self._msg_type

    @property
    def timestamp(self):
        """
        The time stamp of the message.

        :return: The time stamp of the message as datetime object.
        :rtype: datetime
        """
        return self._ts

    @property
    def text(self):
        """
        The text representation of a message.

        :return: A string containing text.
        :rtype: str
        """
        return self._text


class YoutubeMessage:
    """
    Class representing a received youtube message.
    """

    def __init__(self, youtube_data):
        """
        Initialize the class.

        :param youtube_data: The data of the youtube message.
        :type youtube_data: dict
        """
        self._item = youtube_data.get('item')  # type:dict
        self._req = youtube_data.get('req', -1)
        self._ts = datetime.now()

    @property
    def timestamp(self):
        """
        The timestamp of the youtube message.

        :return: The timestamp the youtube was received
        by the client as datetime object.
        :rtype: datetime
        """
        return self._ts

    @property
    def type(self):
        """
        The message type of the youtube.

        NOTE: This will be 3, although it might change
        in a later version.

        :return: The message type.
        :rtype: int
        """
        return 3

    @property
    def is_response(self):
        """
        Is the youtube message a response to a
        client youtube request.

        :return: True if the message is a response to
        a client youtube request, else False.
        :rtype: bool
        """
        if self._req > -1:
            return True

        return False

    @property
    def req(self):
        """
        The req id of the youtube request.

        NOTE: This will be > -1 when the client
        is requesting a youtube.

        :return: The req id of the youtube request.
        :rtype: int
        """
        return self._req

    @property
    def duration(self):
        """
        The duration of the youtube.

        :return: The video duration.
        :rtype: int | float
        """
        return self._item.get('duration')

    @property
    def video_id(self):
        """
        The youtube video id.

        :return: The video id of the youtube.
        :rtype: str
        """
        return self._item.get('id')

    @property
    def image(self):
        """
        A image url of the youtube video.

        :return: A youtube video image url.
        :rtype: str
        """
        return self._item.get('image')

    @property
    def offset(self):
        """
        The youtube video offset.

        :return: The offset of the youtube video.
        :rtype: int | float
        """
        return self._item.get('offset')

    @property
    def playlist(self):
        """
        Indicating if the youtube is part of the playlist.

        :return: True if the youtube is part of the playlist.
        :rtype: bool
        """
        return self._item.get('playlist')

    @property
    def title(self):
        """
        The title of the youtube.

        :return: The title.
        :rtype: str
        """
        return self._item.get('title')
