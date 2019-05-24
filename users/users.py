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

from .banned import BannedUser
from .user import User, UserLevel


class Users(object):
    """
    Class for doing various user related operations.
    """

    def __init__(self):
        """
        Initialize the Users class.

        Creating a dictionary for users and one for banned users.
        """
        # supposedly it is faster to use {}
        self._users = {}
        self._banned_users = {}
        self._client = None

    @property
    def client(self):
        """
        Returns the clients user object.

        :return: The clients user object
        :rtype: User
        """
        return self._client

    @property
    def all(self):
        """
        Returns a dictionary of all the users.

        :return: A dictionary where the key is
        the user handle and the value is User.
        :rtype: dict
        """
        return self._users

    @property
    def mods(self):
        """
        Returns a list of all the moderators.

        :return: A list of moderator User.
        :rtype: list
        """
        mods = []
        for user in self.all:
            if self.all[user].is_mod:
                mods.append(self.all[user])

        return mods

    @property
    def signed_in(self):
        """
        Returns a list of all signed in users.

        :return: A list of all the signed in User
        :rtype: list
        """
        signed_ins = []
        for user in self.all:
            if self.all[user].account:
                signed_ins.append(self.all[user])

        return signed_ins

    @property
    def lurkers(self):
        """
        Returns a list of the lurkers.

        :return: A list of lurkers User.
        :rtype: list
        """
        lurkers = []
        for user in self.all:
            if self.all[user].is_lurker:
                lurkers.append(self.all[user])

        return lurkers

    @property
    def norms(self):
        """
        Returns a list of all normal users,
        e.g users that are not moderators or lurkers.

        :return: A list of all normal User.
        :rtype: list
        """
        regulars = []
        for user in self.all:
            if not self.all[user].is_mod and not self.all[user].is_lurker:
                regulars.append(self.all[user])

        return regulars

    @property
    def broadcasters(self):
        """
        Returns a list of all broadcasting users.

        :return: A list of all the broadcasting User.
        :rtype: list
        """
        broadcasters = []
        for user in self.all:
            if self.all[user].is_broadcasting:
                broadcasters.append(self.all[user])

        return broadcasters

    def clear(self):
        """
        Clear the user dictionary.
        """
        self._users.clear()

    def add(self, user_info, is_client=False):
        """
        Add a user to the user dictionary.

        :param user_info: User information data.
        :type user_info: dict
        :param is_client: Should be True,
        if the user_info is the client's information.
        :type is_client: bool
        :return: The user as User.
        :rtype: User
        """
        handle = user_info['handle']
        if handle not in self.all:
            user = self._users[handle] = User(**user_info)
            if is_client:
                self._client = user
                self._client.user_level = UserLevel.CLIENT

        return self.all[handle]

    def change_nick(self, nick_data):
        """
        Change a users nickname.

        :param nick_data: The nick data dictionary.
        :type nick_data: dict
        :return: The User object of the user.
        :rtype: User
        """
        user = self.all[nick_data['handle']]
        user.nick = nick_data['nick']
        user.old_nicks.append(nick_data['nick'])

        return user

    def add_tc_info(self, handle, account_info):
        """
        Add tinychat information from tinychat's API.

        :param handle: The handle of the user to add info for.
        :type handle: int
        :param account_info: The account information.
        :type account_info: dict
        """
        if handle in self.all:
            user = self.all[handle]
            user.biography = account_info['biography']
            user.gender = account_info['gender']
            user.age = account_info['age']
            user.location = account_info['location']
            user.role = account_info['role']

    def mark_as_approved(self, handle):  # TODO: TEST
        """
        Mark an approved user.

        NOTE: This only marks the user as
        approved for the current session.

        :param handle: The handle of the user to approve.
        :type handle: int
        """
        if handle in self.all:
            user = self.all[handle]
            user.level = UserLevel.APPROVED

    def delete(self, handle):
        """
        Delete a user from the user dictionary.

        :param handle: The handle of the user to delete.
        :type handle: int
        :return: The User object of the deleted user
        or None if the handle was not found.
        :rtype: User | None
        """
        if handle in self.all:
            user = self._users[handle]
            del self._users[handle]
            return user

        return None

    def search(self, handle):
        """
        Search the user dictionary by handle.

        Primary search method, since the user handle is
        present in all(?) user related events.

        :param handle: The handle of the user to find.
        :type handle: int
        :return: The User or None if not found.
        :rtype: User | None
        """
        if handle in self.all:
            return self.all[handle]

        return None

    def search_by_nick(self, nick):
        """
        Search the user dictionary by nick name.

        :param nick: The nick name of the user to search for.
        :type nick: str
        :return: The User or None if not found.
        :rtype: User | None
        """
        for user in self.all:
            if self.all[user].nick == nick:
                return self.all[user]

        return None

    def search_by_account(self, account):
        """
        Search the user dictionary by account.

        :param account: The account to search for.
        :type account: str
        :return: The User or None if not forund.
        :rtype: User | None
        """
        for user in self.all:
            if self.all[user].account == account:
                return self.all[user]

        return None

    def search_containing(self, contains):
        """
        Search the user dictionary for nick names
        matching the search string.

        :param contains: The search string to search for in the nick names.
        :type contains: str
        :return: A list of User matching the search string.
        :rtype: list
        """
        users_containing = []
        for user in self.all:
            if str(contains) in self.all[user].nick:
                users_containing.append(self.all[user])

        return users_containing

    # Banlist related.
    @classmethod
    def _find_most_recent(cls, banned_users):
        """
        Find the most recent banned user in a list of BannedUser objects.

        :param banned_users: A list containing BannedUser objects.
        :type banned_users: list
        :return: A BannedUser object or None.
        :rtype: BannedUser | None
        """
        ban_id = 0
        banned_user = None

        for banned in banned_users:
            if banned.ban_id > ban_id:
                ban_id = banned.ban_id
                banned_user = banned

        return banned_user

    @property
    def banlist(self):
        """
        Returns a dictionary of all banned users.

        :return: A dictionary where the key is
        the ban id and the value is BannedUser.
        :rtype: dict
        """
        return self._banned_users

    @property
    def banned_users(self):
        """
        Returns a list of all the BannedUser objects.

        :return: A list containing BannedUser objects.
        :rtype: list
        """
        banned_users = []
        for banned_user in self.banlist:
            banned_users.append(self.banlist[banned_user])

        return banned_users

    @property
    def banned_accounts(self):
        """
        Returns a list of BannedUser account name.

        :return: A list of BannedUser containing account name.
        :rtype: list
        """
        accounts = []
        for ban_id in self.banlist:
            if self.banlist[ban_id].account:
                accounts.append(self.banlist[ban_id])

        return accounts

    @property
    def last_banned(self):
        """
        Returns the last BannedUser object.

        :return: The last BannedUser object from the banlist.
        :rtype: BannedUser | None
        """
        return self._find_most_recent(self.banned_users)

    def add_banned_user(self, ban_info):
        """
        Add a user to the banned user dictionary.

        :param ban_info: The banned user's ban information.
        :type ban_info: dict
        :return: A BannedUser.
        :rtype: BannedUser
        """
        ban_id = ban_info['id']
        if ban_id not in self.banlist:
            self._banned_users[ban_id] = BannedUser(**ban_info)

        return self.banlist[ban_id]

    def delete_banned_user(self, ban_info):
        """
        Delete a banned user from the banned user dictionary.

        NOTE: This is only possible if the client unban's a user.

        :param ban_info: The banned user's ban information.
        :type ban_info: dict
        :return: The BannedUser or None if not in the dictionary.
        :rtype: BannedUser | None
        """
        ban_id = ban_info['id']
        if ban_id in self.banlist:
            banned_user = self.banlist[ban_id]
            del self._banned_users[ban_id]

            return banned_user

        return None

    def clear_banlist(self):
        """
        Clear the ban list.
        """
        self._banned_users.clear()

    def search_banlist(self, ban_id):
        """
        Search the banlist dictionary by ban id.

        NOTE: Not implemented.

        :param ban_id: The ban id to search for.
        :type ban_id: int
        :return: A BannedUser or None if not found.
        :rtype: BannedUser | None
        """
        if ban_id in self.banlist:
            return self.banlist[ban_id]

        return None

    def search_banlist_by_nick(self, user_name):
        """
        Search the banlist for a username.

        If more than one username match is found,
        then the most recent BannedUser object will be returned.

        :param user_name: The user name of the banned user to search for.
        :type user_name: str
        :return: A BannedUser object or None if no match was found in the banlist.
        :rtype: BannedUser | None
        """
        candidates = []
        for ban_id in self.banlist:
            if self.banlist[ban_id].nick == user_name:
                candidates.append(self.banlist[ban_id])

        if len(candidates) == 0:
            return None

        return self._find_most_recent(candidates)

    def search_banlist_by_account(self, account):
        """
        Search the banlist by account.

        NOTE: Test this.

        :param account: The account to search for.
        :type account: str
        :return: A banned user matching the account.
        :rtype: BannedUser
        """
        for ban_id in self.banlist:
            if self.banlist[ban_id].account == account:
                return self.banlist[ban_id]

        return None

    def search_banlist_containing(self, contains):
        """
        Search the banlist for user names matching the search str.

        :param contains: The search term to search for.
        :type contains: str
        :return: A list of matches.
        :rtype: list
        """
        banned_containing = []
        for user in self.banlist:
            if str(contains) in self.banlist[user].nick:
                banned_containing.append(self.banlist[user])

        return banned_containing

    def search_banlist_by_moderator(self, moderator):
        """
        Search the banlist for users banned by a specific moderator.

        :param moderator: The moderator users should have been banned by.
        :type moderator: str
        :return: A list of BannedUser objects.
        :rtype: list
        """
        banned_by_mod = []
        for ban_id in self.banlist:
            if self.banlist[ban_id].banned_by == moderator:
                banned_by_mod.append(self.banlist[ban_id])

        return banned_by_mod
