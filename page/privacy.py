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


class Privacy:
    """
    This class represents tinychat's privacy page for a room,
    it contains methods to change a rooms privacy settings.
    """
    _privacy_url = 'https://tinychat.com/settings/privacy'

    def __init__(self, proxy=None):
        """
        Create a instance of the Privacy class.

        :param proxy: A proxy in the format IP:PORT
        :type proxy: str | None
        """
        self._proxy = proxy
        self._csrf_token = None
        self._room_password = None
        self._room_pass_enabled = 0
        self._broadcast_password = None
        self._broadcast_pass_enabled = 0
        self._room_moderators = []
        self._form_data = {}
        self._soup = None

    @property
    def room_moderators(self):
        """
        Returns the moderator list for a room.

        :return: A list of moderators.
        :rtype: list
        """
        return self._room_moderators

    def _clear_bans(self):
        """
        Clear all room bans.

        NOTE: This method does not seem to be supported
        by tinychat anymore.

        :return: True if bans were cleared, else False.
        :rtype: bool
        """
        header = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self._privacy_url
        }
        form_data = {'_token': self._csrf_token}

        url = 'https://tinychat.com/settings/privacy/clearbans'
        response = web.post(url=url, data=form_data,
                            headers=header, as_json=True, proxy=self._proxy)

        if len(response.errors) > 0:
            log.error(response.errors)
            return False
        else:
            if not response.json['error']:
                if response.json['response'] == 'Bans cleared':
                    return True

            return False

    def parse_settings(self, response=None):

        if response is None:
            response = web.get(url=self._privacy_url,
                               referer=self._privacy_url, proxy=self._proxy)

        if len(response.errors) > 0:
            log.error(response.errors)
        else:
            self._soup = BeautifulSoup(response.content, 'html.parser')
            if self._parse_csrf_token():
                self._parse_guest_setting()
                self._parse_directory_setting()
                self._parse_push2talk_setting()
                self._parse_greenroom_setting()
                self._parse_room_pass_setting()
                self._parse_broadcast_pass_setting()
                self._parse_moderators(response)

    def set_room_password(self, password=None):
        """
        Set a room password or clear the password.

        :param password: The room password or None to clear.
        :type password: str | None
        """
        if password is None:
            self._room_password = ''
        else:
            self._room_password = password

        if self._broadcast_password is None:
            self._broadcast_password = ''

        form_data = {
            'roomPassword': self._room_password,
            'broadcastPassword': self._broadcast_password,
            'privacy_password': 1,
            '_token': self._csrf_token
        }
        response = web.post(url=self._privacy_url, data=form_data,
                            referer=self._privacy_url)

        self.parse_settings(response=response)

    def set_broadcast_password(self, password=None):
        """
        Set a broadcast password or clear the password.

        :param password: The broadcast password or None to clear.
        :type password: str | None
        """
        if password is None:
            self._broadcast_password = ''
        else:
            self._broadcast_password = password

        if self._room_password is None:
            self._room_password = ''

        form_data = {
            'roomPassword': self._room_password,
            'broadcastPassword': self._broadcast_password,
            'privacy_password': 1,
            '_token': self._csrf_token
        }
        response = web.post(url=self._privacy_url, data=form_data,
                            referer=self._privacy_url)

        self.parse_settings(response=response)

    def make_moderator(self, account):
        """
        Make a user account a moderator.

        :param account: The account to make a moderator.
        :type account: str
        :return True if the account was added as a moderator, False if already a moderator
        or None on invalid account name or error.
        :rtype: bool | None
        """
        url = 'https://tinychat.com/settings/privacy/addfeatureduser'
        if self._is_valid_account(account):
            if account not in self.room_moderators:

                form_data = {
                    '_token': self._csrf_token,
                    'name': account,
                    'type': 'moderator'
                }
                response = web.post(url=url, data=form_data,
                                    as_json=True, proxy=self._proxy)

                if len(response.errors) > 0:
                    log.error(response.errors)
                    return None
                else:
                    if not response.json['error'] and response.json['response'] == 'Data added':
                        self.parse_settings()
                        if account in self.room_moderators:
                            return True

            return False

        return None

    def remove_moderator(self, account):
        """
        Remove a room moderator.

        :param account: The moderator account to remove.
        :return: True if removed else False
        :rtype: bool
        """
        url = 'https://tinychat.com/settings/privacy/removefeatureduser'
        if account in self.room_moderators:

            form_data = {
                '_token': self._csrf_token,
                'name': account,
                'type': 'moderator'
            }
            response = web.post(url=url, data=form_data,
                                as_json=True, proxy=self._proxy)
            if len(response.errors) > 0:
                log.error(response.errors)
                return None
            else:
                if not response.json['error'] and response.json['response'] == 'Data removed':
                    self._room_moderators.remove(account)
                    return True
        return False

    def set_guest_mode(self):
        """
        Enable/disable guest mode.

        :return: True if guests are allowed, else False.
        :rtype: bool
        """
        if not self._form_data['allow_guest']:
            self._form_data['allow_guest'] = 1
            self._update()
            return True
        elif self._form_data['allow_guest']:
            self._form_data['allow_guest'] = 0
            self._form_data['require_twitter'] = 0
            self._form_data['require_facebook'] = 0
            self._update()
            return False

    def set_guest_mode_twitter(self):
        """
        Enable/disable guest mode twitter.

        :return: True if guest mode is set to twitter, else False.
        :rtype: bool
        """
        if self._form_data['allow_guest']:
            if not self._form_data['require_twitter']:
                self._form_data['require_twitter'] = 1
                self._update()
                return True
            elif self._form_data['require_twitter']:
                self._form_data['require_twitter'] = 0
                self._update()
                return False
        else:
            self._form_data['allow_guest'] = 1
            self._form_data['require_twitter'] = 1
            self._update()
            return True

    def set_guest_mode_facebook(self):
        """
        Enable/disable guest mode facebook.

        :return: True if guest mode is set to facebook, else False.
        :rtype: bool
        """
        if self._form_data['allow_guest']:
            if not self._form_data['require_facebook']:
                self._form_data['require_facebook'] = 1
                self._update()
                return True
            elif self._form_data['require_facebook']:
                self._form_data['require_facebook'] = 0
                self._update()
                return False
        else:
            self._form_data['allow_guest'] = 1
            self._form_data['require_facebook'] = 1
            self._update()
            return True

    def show_on_directory(self):
        """
        Enables/disables show up on directory setting.

        :return: True if enabled else False.
        :rtype: bool
        """
        if not self._form_data['public_directory']:
            self._form_data['public_directory'] = 1
            self._update()
            return True
        elif self._form_data['public_directory']:
            self._form_data['public_directory'] = 0
            self._update()
            return False

    def set_push2talk(self):
        """
        Enables/disables push2talk setting.

        :return: True if enabled else False.
        :rtype: bool
        """
        if not self._form_data['push2talk']:
            self._form_data['push2talk'] = 1
            self._update()
            return True
        elif self._form_data['push2talk']:
            self._form_data['push2talk'] = 0
            self._update()
            return False

    def set_greenroom(self):
        """
        Enables/disables greenroom setting.

        :return: True if enabled else False.
        :rtype: bool
        """
        if not self._form_data['greenroom']:
            self._form_data['greenroom'] = 1
            self._update()
            return True
        elif self._form_data['greenroom']:
            self._form_data['greenroom'] = 0
            self._update()
            return False

    def current_settings(self):
        """
        Returns a dictionary of the current room settings.

        :return dictionary with the keys: `broadcast_pass`, `room_pass`,
        `allow_guest`, `show_on_directory`, `push2talk`, `greenroom`
        :rtype: dict
        """
        self.parse_settings()

        settings = {}
        if self._broadcast_password or self._broadcast_pass_enabled:
            settings['broadcast_pass'] = 'Enabled'
        else:
            settings['broadcast_pass'] = 'Disabled'
        if self._room_password or self._room_pass_enabled:
            settings['room_pass'] = 'Enabled'
        else:
            settings['room_pass'] = 'Disabled'

        settings['allow_guest'] = 'No login required'  #
        if self._form_data['allow_guest']:
            if self._form_data['require_twitter'] and self._form_data['require_facebook']:
                settings['allow_guest'] = 'Twitter/Facebook'
            elif self._form_data['require_twitter']:
                settings['allow_guest'] = 'Twitter'
            elif self._form_data['require_facebook']:
                settings['allow_guest'] = 'Facebook'
        if self._room_password:
            settings['show_on_directory'] = 'Hidden'
        else:
            if self._form_data['public_directory']:
                settings['show_on_directory'] = 'Public'
            else:
                settings['show_on_directory'] = 'Hidden'
        if self._form_data['push2talk']:
            settings['push2talk'] = 'Enabled'
        else:
            settings['push2talk'] = 'Disabled'
        if self._form_data['greenroom']:
            settings['greenroom'] = 'Enabled'
        else:
            settings['greenroom'] = 'Disabled'

        return settings

    @staticmethod
    def _is_valid_account(account):
        """
        Helper method to check if a user account is a valid account name.

        :param account: The account name to check.
        :type account: str
        :return: True if it is a valid account, else False.
        :rtype: bool
        """
        url = 'https://tinychat.com/api/v1.0/user/profile?username={0}&'.format(account)
        response = web.get(url=url, as_json=True)

        if len(response.errors) > 0:
            log.error(response.errors)
        else:
            if response.json['result'] == 'success':
                return True
            return False

    def _parse_csrf_token(self):
        token = self._soup.find(attrs={'name': 'csrf-token'})
        self._csrf_token = token['content']

        if self._csrf_token is not None:
            log.debug('csrf token parsed: %s' % self._csrf_token)
            return True
        return False

    def _parse_guest_setting(self):
        guest_settings = self._soup.find('input', {'name': 'allow_guest', 'checked': True})
        if guest_settings is not None:
            self._form_data['allow_guest'] = 1
            twitter = self._soup.find('input', {'name': 'require_twitter', 'checked': True})
            if twitter is not None:
                self._form_data['require_twitter'] = 1
            else:
                self._form_data['require_twitter'] = 0
            facebook = self._soup.find('input', {'name': 'require_facebook', 'checked': True})
            if facebook is not None:
                self._form_data['require_facebook'] = 1
            else:
                self._form_data['require_facebook'] = 0
        else:
            self._form_data['allow_guest'] = 0
            self._form_data['require_twitter'] = 0
            self._form_data['require_facebook'] = 0

    def _parse_directory_setting(self):
        dir_settings = self._soup.find('input', {'name': 'public_directory', 'checked': True})
        if dir_settings is not None:
            self._form_data['public_directory'] = 1
        else:
            self._form_data['public_directory'] = 0

    def _parse_push2talk_setting(self):
        push2talk = self._soup.find('input', {'name': 'push2talk', 'checked': True})
        if push2talk is not None:
            self._form_data['push2talk'] = 1
        else:
            self._form_data['push2talk'] = 0

    def _parse_greenroom_setting(self):
        greenroom = self._soup.find('input', {'name': 'greenroom', 'checked': True})
        if greenroom is not None:
            self._form_data['greenroom'] = 1
        else:
            self._form_data['greenroom'] = 0

    def _parse_room_pass_setting(self):
        room_pass = self._soup.find(attrs={'name': 'roomPassword'})
        if room_pass['value']:
            self._room_pass_enabled = 1
        else:
            self._room_pass_enabled = 0

    def _parse_broadcast_pass_setting(self):
        # TODO: make sure this works as expected
        if not self._form_data['greenroom']:
            # broadcast password
            broadcast_pass = self._soup.find(attrs={'name': 'broadcastPassword'})
            if broadcast_pass['value']:
                self._broadcast_pass_enabled = 1
            else:
                self._broadcast_pass_enabled = 0

    def _parse_moderators(self, response):
        pattern = 'var moderators = \''
        if pattern in response.content:
            mod_str = str(response.content).split(pattern)[1].split('\';')[0].replace('"', '\'')
            mod_str_replaced = mod_str.replace('[', '').replace(']', '').replace('\'', '')
            mods = mod_str_replaced.split(',')
            if len(mods) > 0:
                for mod in mods:
                    if mod != '' and mod not in self._room_moderators:
                        self._room_moderators.append(mod)

    def _update(self):
        """
        Update the privacy page with the current settings.

        This is called when ever a change is made.
        """
        self._form_data['privacy_changes'] = 1
        self._form_data['_token'] = self._csrf_token

        if not self._form_data['allow_guest']:
            del self._form_data['allow_guest']
        if not self._form_data['require_twitter']:
            del self._form_data['require_twitter']
        if not self._form_data['require_facebook']:
            del self._form_data['require_facebook']
        if not self._form_data['public_directory']:
            del self._form_data['public_directory']
        if not self._form_data['push2talk']:
            del self._form_data['push2talk']
        if not self._form_data['greenroom']:
            del self._form_data['greenroom']

        response = web.post(url=self._privacy_url, data=self._form_data,
                            referer=self._privacy_url, proxy=self._proxy)

        self.parse_settings(response=response)
