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
from util import web

log = logging.getLogger(__name__)


class TinychatApi(object):

    @classmethod
    def rtc_version(cls, room):
        """
        Parse the current tinychat RTC version.

        :param room: This could be a static room name,
        since we just need the html of any room.
        :type room: str
        :return: The current tinychat rtc version, or None on parse failure.
        :rtype: str | None
        """
        url = 'https://tinychat.com/room/{0}'.format(room)
        response = web.get(url=url)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            pattern = '<link rel="manifest" href="/webrtc/'
            return response.content.split(pattern)[1].split('/manifest.json">')[0]

    @classmethod
    def connect_token(cls, room):
        """
        Get the connect token and the wss server endpoint.

        :param room: The room to get the details for.
        :type room: str
        :return: The token and the wss endpoint.
        :rtype: dict | None
        """
        url = 'https://tinychat.com/api/v1.0/room/token/{0}'.format(room)

        response = web.get(url, as_json=True)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            # more strict error checking?
            return {
                'token': response.json['result'],
                'endpoint': response.json['endpoint']
            }

    @classmethod
    def user_info(cls, account):
        """
        Get the user information related to the account name.

        :param account: The tinychat account name.
        :type account: str
        :return: A dictionary containing info about the user account.
        :rtype: dict | None
        """
        url = 'https://tinychat.com/api/v1.0/user/profile?username={0}&'.format(account)
        response = web.get(url, as_json=True)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            if response.json['result'] == 'success':
                return {
                    'biography': response.json['biography'],
                    'gender': response.json['gender'],
                    'location': response.json['location'],
                    'role': response.json['role'],
                    'age': response.json['age']
                }

            return None
