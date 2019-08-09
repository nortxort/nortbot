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
from datetime import datetime
from util import Timer

log = logging.getLogger(__name__)

# valid yes/no votes
YES = ['1', 'true', 'True', 'YES', 'Yes', 'yes', 'y', 'Y']
NO = ['0', 'false', 'False', 'NO', 'No', 'no', 'n', 'N']


class Vote:
    def __init__(self, bot):
        self._bot = bot
        self._current_room_users = self._sort_user_by_join_time(self._bot.users.all)
        self._has_voted = []    # user handle of the users who voted
        self._votes = []        # list of tuple(User, vote)

        self._user_to_vote = None
        self._vote_session = 0
        self._vote_type = ''
        self._vote_timer = None

    @property
    def is_active(self):
        """
        Check for active vote session.

        :return: True if active vote session.
        :rtype: bool
        """
        return self._has_active_session()

    @property
    def has_voted(self):
        """
        Returns a list of user handles that have already voted.

        :return: A list of user handles.
        :rtype: list
        """
        return self._has_voted

    @property
    def vote_user(self):
        """
        Return the User object of the user up for vote.

        :return: The User object of the user up for vote.
        :rtype: User
        """
        return self._user_to_vote

    @property
    def active_vote_type(self):
        """
        Return the type of vote session.

        :return: Type of vote session.
        :rtype: str
        """
        return self._vote_type

    def vote(self, user, vote):
        """
        Add a vote to the vote session.

        :param user: A User object.
        :type user: User
        :param vote: A yes/no vote.
        :type vote: str
        :return: True if the vote was accepted.
        :rtype: bool
        """
        if self._can_vote(user):
            if vote in YES or vote in NO:
                # there might not be a reason to store the user
                self._votes.append((user, vote))
                self._has_voted.append(user.handle)

                return True

        return False

    @staticmethod
    def can_start(user, seconds=300):
        """
        Helper method to check if a user is allowed
        to start the vote session.

        The intention was, that this method should
        be called before start(), to check if the
        user wanting to start the vote session,
        have been in the room long enough.

        :param user: The user to check.
        :type user: User
        :param seconds: The time the user must have been in the room.
        :type seconds: int
        :return: True if the user is allowed to start the session.
        :rtype: bool
        """
        now = datetime.now()

        dif = now - user.join_time
        if dif.seconds > seconds:
            return True

        return False

    def start(self, user_to_vote, session, vote_type):
        """
        Start the voting session.

        :param user_to_vote: The user up for voting.
        :type user_to_vote: User
        :param session: The session time in seconds.
        :type session: int
        :param vote_type: The type of vote.
        :type vote_type: str
        :return: True if the vote session was started
        :rtype: bool
        """
        log.debug('%s, session=%s, vote_type=%s' %
                  (user_to_vote, session, vote_type))

        if not self._has_active_session():
            self._user_to_vote = user_to_vote
            self._vote_session = session
            self._vote_type = vote_type

            # start the timer
            self._vote_timer = Timer()
            self._vote_timer.start(self._decide_vote, self._vote_session)

            return True

        return False

    def cancel(self):
        """
        Cancel the vote session.

        :return: True if canceled.
        :rtype: bool
        """
        if self._has_active_session():
            return self._vote_timer.cancel()

        return False

    def _sort_user_by_join_time(self, users):
        # only allow users who have been in the room
        # for more than 5 minutes(300seconds) to vote
        sorted_users = {}
        now = datetime.now()

        for handle in users:
            dif = now - users[handle].join_time
            if dif.seconds > 300:
                # do not add the bot itself
                if handle != self._bot.users.client.handle:
                    sorted_users[handle] = users[handle]

        return sorted_users

    def _can_vote(self, user):
        # was the user among the room users
        # when the vote session was started
        if user.handle in self._current_room_users:
            # has the user already voted
            if user.handle not in self._has_voted:
                return True

        return False

    def _has_active_session(self):
        # is there an active vote session running
        if self._vote_timer is not None:
            if isinstance(self._vote_timer, Timer):
                if self._vote_timer.is_alive:
                    return True

        return False

    def _was_vote_yes(self):
        # the result of the votes, True if yes, False on tie or no
        # Thanks to notnola (https://github.com/notnola/pinychat)
        yes = 0
        no = 0
        for _, vote in self._votes:

            if vote in YES:
                yes += 1
            else:
                no += 1

        return yes > no

    def _calculate_vote_percentage(self):
        # calculate the voting percentage
        return len(self._has_voted) * 100 / len(self._current_room_users)

    def _decide_vote(self):
        # decide based on vote percentage and votes
        percentage = self._calculate_vote_percentage()
        # at least 1/3 or the room should have voted. maybe adjust this
        if percentage >= 33:
            if self._was_vote_yes():
                self._bot.responder('With %s voters (%s%%) the room has decided to %s %s.' %
                                    (len(self._has_voted), percentage, self._vote_type,
                                     self._user_to_vote.nick))
                self._vote_action()
            else:
                self._bot.responder('With %s voters (%s%%) the room has decided NOT to %s %s.' %
                                    (len(self._has_voted), percentage, self._vote_type,
                                     self._user_to_vote.nick))
        else:
            self._bot.responder('With %s voters (%s%%) there were not '
                                'enough votes to make a decision.' %
                                (len(self._has_voted), percentage))

    def _vote_action(self):
        # initiate the action of the vote, based on vote type
        user = self._bot.users.search(self._user_to_vote.handle)
        if user is None:
            user = self._bot.users.search_by_nick(self._user_to_vote.nick)

        log.debug('%s' % user)
        if user is not None:

            if self._vote_type == 'ban':
                self._bot.send_ban_msg(user.handle)

            elif self._vote_type == 'kick':
                self._bot.send_kick_msg(user.handle)

            elif self._vote_type == 'close':
                if user.is_broadcasting:
                    self._bot.send_close_user_msg(user.handle)
                # prevent further user cam
                user.can_broadcast = False
        # else:
        #     self._bot.responder('%s ran like a dog.' % self._user_to_vote.nick)
