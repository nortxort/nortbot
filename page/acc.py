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


class Account:
    """
    This class contains methods to do login/logout and check if logged in or not.
    """

    def __init__(self, account, password, proxy=None):
        """
        Create a instance of the Account class.

        :param account: Tinychat account name.
        :type account: str
        :param password: Tinychat account password.
        :type password: str
        :param proxy: A proxy in the format IP:PORT
        :type proxy: str
        """
        self.account = account
        self.password = password
        self._proxy = proxy
        self._token = None

    def _parse_token(self, response=None):
        """
        Parse the token needed for the HTTP login POST.

        :param response: A Response object.
        :type response: web.Response
        """
        token_url = 'https://tinychat.com/start?#signin'
        if response is None:
            response = web.get(
                url=token_url, referer=token_url, proxy=self._proxy)

        if len(response.errors) > 0:
            log.error(response.errors)
        else:
            soup = BeautifulSoup(response.content, 'html.parser')

            token = soup.find(attrs={'name': 'csrf-token'})
            self._token = token['content']

    @staticmethod
    def logout():
        """
        Log out of tinychat.
        """
        cookies = ['user', 'pass', 'hash']
        for cookie in cookies:
            web.WebSession.delete_cookie(cookie)

    @staticmethod
    def is_logged_in():
        """
        Check if logged in to tinychat.

        :return True if logged in, else False.
        :rtype: bool
        """
        has_cookie = web.WebSession.has_cookie('pass')
        if has_cookie:
            is_expired = web.WebSession.is_cookie_expired('pass')
            if is_expired:
                return False
            return True
        return False

    def login(self):
        """
        Makes a HTTP login POST to tinychat.
        """
        if self._token is None:
            self._parse_token()

        url = 'https://tinychat.com/login'

        form_data = {
            'login_username': self.account,
            'login_password': self.password,
            'remember': '1',
            'next': 'https://tinychat.com/',
            '_token': self._token
        }

        login_response = web.post(url=url, data=form_data, proxy=self._proxy)

        self._parse_token(response=login_response)

        return self.is_logged_in()
