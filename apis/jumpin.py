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
from bs4 import BeautifulSoup
from util import web

log = logging.getLogger(__name__)


class User:
    """
    Class representing a user on jumpin.chat
    """
    def __init__(self, **user_data):
        self._data = user_data

    @property
    def account(self):
        return self._data.get('username', None)

    @property
    def operator_id(self):
        return self._data.get('operator_id', '')

    @property
    def user_id(self):
        return self._data.get('user_id', '')

    @property
    def color(self):
        return self._data.get('color', '')

    @property
    def is_supporter(self):
        return self._data.get('isSupporter', False)

    @property
    def assigned_by(self):
        return self._data.get('assignedBy', '')

    @property
    def is_admin(self):
        return self._data.get('isAdmin', False)

    @property
    def is_broadcasting(self):
        return self._data.get('isBroadcasting', False)

    @property
    def nick(self):
        # chat nick
        return self._data.get('handle', '')

    @property
    def _id(self):
        return self._data.get('_id', '')

    @property
    def user_icon(self):
        return self._data.get('userIcon', '')


class Room:
    """
    Class representing a room on jumpin.chat

    NOTE: more information could possibly be added.
    """
    def __init__(self, **data):
        self._data = data

    @property
    def name(self):
        return self._data.get('name', '')

    @property
    def is_private(self):
        return self._data.get('public', False)

    @property
    def force_users(self):
        return self._data.get('forceUser', False)

    @property
    def public(self):
        return self._data.get('public', False)

    @property
    def age_restricted(self):
        return self._data.get('ageRestricted', False)

    @property
    def settings(self):
        return self._data.get('settings', None)

    @property
    def users(self):
        _ = []

        users = self._data.get('users', [])
        if len(users) > 0:
            for user in users:
                _user = User(**user)
                _.append(_user)

        return _


class JumpinChatApi(object):
    """
    Class for doing various jumpin.chat Api calls.
    """
    _token = None
    _directory_rooms = []
    _soup = None

    @classmethod
    def room(cls, room_name):
        """
        Get the information of a room as Room object.

        :param room_name: The room name to find information for.
        :type room_name: str
        :return: A Room object.
        :rtype: Room
        """
        if len(room_name.strip()) != 0:
            return cls._room_details(room_name)

        return None

    @classmethod
    def directory(cls):
        """
        Get the current rooms on the directory.

        :return: A list of Rooms.
        :rtype: list
        """
        return cls._directory()

    @classmethod
    def user_search(cls, account):
        """
        Search for a user on jumpin.chat

        :param account: The user account to search for.
        :type account: str
        :return: A list of rooms the user was found in.
        :rtype: list
        """
        _rooms = []
        dir_rooms = cls._directory()

        if len(dir_rooms) > 0:
            for room in dir_rooms:
                for user in room.users:
                    if account == user.account:
                        _rooms.append(room)

        return _rooms

    # Private methods
    @classmethod
    def _room_details(cls, room_name):
        # get the room details of a room
        if cls._token is None:
            cls._set_token()

        url = 'https://jumpin.chat/api/rooms/%s' % room_name
        response = web.get(url=url, as_json=True)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            room = Room(**response.json)
            if len(room.users) > 0:
                return room

            return None

    @classmethod
    def _directory(cls):
        # parse the first page on the directory
        # and start parsing pages, should there be any more
        url = 'https://jumpin.chat/directory'
        response = web.get(url=url)

        # make sure there is no previous rooms
        cls._directory_rooms[:] = []

        if len(response.errors) > 0:
            log.error(response.errors)
        else:
            cls._soup = BeautifulSoup(response.content, 'html.parser')

            # get the rooms from the current page(1) on the directory
            for room_name in cls._parse_page_rooms():

                room_details = cls._room_details(room_name)
                if room_details is not None:
                    cls._directory_rooms.append(room_details)

            # loop over the pages in the directory
            cls._iter_dir_pages()

        return cls._directory_rooms

    @classmethod
    def _iter_dir_pages(cls):
        # iterate through the pages(if any) on the directory
        pages = cls._get_page_numbers()

        if len(pages) > 1:
            for n in pages[1:]:
                url = 'https://jumpin.chat/directory/?page=%s' % n
                response = web.get(url=url)

                if len(response.errors) > 0:
                    log.error(response.errors)
                else:
                    cls._soup = BeautifulSoup(response.content, 'html.parser')

                    for room_name in cls._parse_page_rooms():

                        room_details = cls._room_details(room_name)
                        if room_details is not None:
                            cls._directory_rooms.append(room_details)

        cls._soup = None

    @classmethod
    def _parse_page_rooms(cls):
        # parse rooms from the soup
        _ = []
        if cls._soup is not None:
            rooms = cls._soup.find_all(attrs={'class': 'room__Name'})
            for r in rooms:
                room_name = r['title']
                if room_name not in _:
                    _.append(room_name)

        return _

    @classmethod
    def _get_page_numbers(cls):
        # returns the number of pages on the directory as a list of int
        _ = []
        if cls._soup is not None:
            pagination = cls._soup.find(attrs={'class': 'pagination'})
            pages = pagination.find_all(attrs={'class': 'pagination__Page'})

            for p in pages:
                try:
                    _.append(int(p.text))
                except ValueError:
                    break

        return _

    @classmethod
    def _set_token(cls):
        # set the token needed before we can get room details
        url = 'https://jumpin.chat/api/user/'
        response = web.get(url=url, as_json=True)

        if len(response.errors) > 0:
            log.error(response.errors)

        elif 'token' in response.json:
            cls._token = response.json['token']
