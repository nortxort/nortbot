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


class RoomState:
    """
    This class holds a rooms state.

    The state is basically a room's profile information.
    It will be updated once the room has been joined by
    the client, or if settings to the privacy page
    are made.
    """

    def __init__(self):
        self._avatar = ''
        self._biography = ''
        self._giftpoints = 0
        self._location = ''
        self._name = ''
        self._push2talk = False
        self._recent_gifts = []
        self._subscription = 0
        self._topic = ''
        self._type = 'default'
        self._website = ''
        self._greenroom = False

    def update(self, **kwargs):
        """
        Update the state of the room.

        :param kwargs: The settings as dictionary.
        :type kwargs: dict
        """
        self._avatar = kwargs.get('avatar', '')
        self._biography = kwargs.get('biography', '')
        self._giftpoints = kwargs.get('giftpoints', 0)
        self._location = kwargs.get('location', '')
        self._name = kwargs.get('name', '')
        self._push2talk = kwargs.get('pushtotalk', False)
        self._recent_gifts = kwargs.get('recent_gifts', [])
        self._subscription = kwargs.get('subscription', 0)
        self._topic = kwargs.get('topic', '')
        self._type = kwargs.get('type', 'default')
        self._website = kwargs.get('website', '')

    def set_greenroom(self, state):
        """
        Set the green room state of the room.

        :param state: The green room state.
        :type state: bool
        """
        self._greenroom = state

    @property
    def is_green_room(self):
        """
        Indicating if a room is in green room mode.

        :return: True if in green room mode.
        :rtype: bool
        """
        return self._greenroom

    @property
    def avatar(self):
        """
        The rooms avatar.

        :return: The avatar url.
        :rtype: str
        """
        return self._avatar

    @property
    def bio(self):
        """
        The rooms biography.

        :return: The rooms biography.
        :rtype: str
        """
        return self._biography

    @property
    def giftpoints(self):
        """
        The room's gift points.

        :return: The rooms gift points as integer.
        :rtype: int
        """
        return self._giftpoints

    @property
    def location(self):
        """
        Room's location.

        :return: The location of the room(account)
        :rtype: str
        """
        return self._location

    @property
    def name(self):
        """
        Room's Name.

        :return: The room's name.
        :rtype: str
        """
        return self._name

    @property
    def pushtotalk(self):
        """
        The room's push to talk state.

        :return: True if the room has push to talk enabled.
        :rtype: bool
        """
        return self._push2talk

    @property
    def gifts(self):
        """
        Recent room gifts.

        :return: A list a gifts the room has received.
        :rtype: list
        """
        return self._recent_gifts

    @property
    def subscription(self):
        """
        Room subscribers.

        :return: The amount of subscribers the room has.
        :rtype: int
        """
        return self._subscription

    @property
    def topic(self):
        """
        Room topic.

        :return: The topic of the room.
        :rtype: str
        """
        return self._topic

    @property
    def type(self):
        """
        The room type.

        NOTE: Seems to always be `default`

        :return: The type of room.
        :rtype: str
        """
        return self._type

    @property
    def website(self):
        """
        The website of the room(if any)

        :return: A website domain.
        :rtype: str
        """
        return self._website

    def formatted(self):
        """
        A formatted representation of (some) of
        the state settings.

        :return: The settings formatted with line breaks.
        :rtype: str
        """
        settings = 'Avatar: {0}\n' \
                   'Biography: {1}\n' \
                   'Gift points: {2}\n' \
                   'Location: {3}\n' \
                   'Name: {4}\n' \
                   'PushToTalk: {5}\n' \
                   'Green Room: {6}\n' \
                   'Website: {7}'.format(self.avatar, self.bio,
                                         self.giftpoints, self.location,
                                         self.name, self.pushtotalk,
                                         self.is_green_room, self.website)

        return settings
