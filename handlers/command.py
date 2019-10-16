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

from users import UserLevel
from util import string_util, file_handler, thread_task
from apis import Youtube, TinychatApi, JumpinChatApi, WikiPedia, lastfm, locals_, other
from lc import LiveCount
from vote import Vote

log = logging.getLogger(__name__)


class CommandHandler:
    def __init__(self, bot, user, msg, config, pool):
        self._bot = bot
        self._user = user
        self._msg = msg
        self._conf = config
        self._pool = pool

        self._playlist = bot.playlist

    def handle(self):
        """
        Handle command.
        """
        if self._msg.text.startswith(self._conf.PREFIX):

            parts = self._msg.text.split(' ')
            cmd = parts[0].lstrip(self._conf.PREFIX).lower().strip()
            cmd_arg = ' '.join(parts[1:]).strip()

            self._handle_command(cmd, cmd_arg)

    def _responder(self, msg, timeout=0.0):
        self._bot.responder(msg, msg_type=self._msg.type,
                            user=self._user, timeout=timeout)

    def _handle_command(self, cmd, cmd_arg):
        log.debug('handling command `%s`, args: %s, user: %s' %
                  (cmd, cmd_arg, self._user))

        if self._user.level == UserLevel.OWNER:

            if self._bot.users.client.is_owner:

                if cmd == 'mod':
                    self._pool.add_task(self.do_make_mod, cmd_arg)

                elif cmd == 'rmod':
                    self._pool.add_task(self.do_remove_mod, cmd_arg)

                elif cmd == 'dir':
                    self._pool.add_task(self.do_directory)

                elif cmd == 'p2t':
                    self._pool.add_task(self.do_push2talk)

                elif cmd == 'crb':
                    self._bot.send_chat_msg('command `crb` is not supported.')

            if cmd == 'key':
                self.do_key(cmd_arg)

            elif cmd == 'clrbn':
                self.do_clear_bad_nicks()

            elif cmd == 'clrbs':
                self.do_clear_bad_strings()

            elif cmd == 'clrba':
                self.do_clear_bad_accounts()

            elif cmd == 'clrap':
                self.do_clear_approved_users()

            elif cmd == 'kill':
                self.do_kill()

            elif cmd == 'reboot':
                self.do_reboot()

        if self._user.level <= UserLevel.SUPER:

            if cmd == 'mi':
                self.do_media_info()

            elif cmd == 'dev':
                self.do_dev()

        if self._user.level <= UserLevel.MODERATOR:

            if cmd == 'op':
                self.do_op_user(cmd_arg)

            elif cmd == 'deop':
                self.do_deop_user(cmd_arg)

            elif cmd == 'apr':
                self.do_approve(cmd_arg)

            elif cmd == 'dapr':
                self.do_de_approve(cmd_arg)

            elif cmd == 'bb':
                self.do_banned_by(cmd_arg)

            elif cmd == 'noguest':
                self.do_guests()

            elif cmd == 'lurkers':
                self.do_lurkers()

            elif cmd == 'guestnick':
                self.do_guest_nicks()

            elif cmd == 'greet':
                self.do_greet()

            elif cmd == 'pub':
                self.do_public_cmds()

            elif cmd == 'kab':
                self.do_kick_as_ban()

            elif cmd == 'nob':
                self.do_notify_on_ban()

            elif cmd == 'vip':
                self.do_vip_mode()

            elif cmd == 'vo':  # new
                self.do_voting()

            elif cmd == 'rs':
                self.do_room_settings()

            elif cmd == 'top':
                self._pool.add_task(self.do_lastfm_chart, cmd_arg)

            elif cmd == 'ran':
                self._pool.add_task(self.do_lastfm_random_tunes, cmd_arg)

            elif cmd == 'tag':
                self._pool.add_task(self.do_search_lastfm_by_tag, cmd_arg)

            elif cmd == 'pls':
                self._pool.add_task(self.do_youtube_playlist_search, cmd_arg)

            elif cmd == 'plp':
                self._pool.add_task(self.do_play_youtube_playlist, cmd_arg)

            elif cmd == 'ssl':
                self.do_show_search_list()

        if self._user.level <= UserLevel.APPROVED:

            if cmd == 'skip':
                self.do_skip()

            elif cmd == 'del':
                self.do_delete_playlist_item(cmd_arg)

            elif cmd == 'rpl':
                self.do_media_replay()

            elif cmd == 'mbpl':
                self.do_play_media()

            elif cmd == 'mbpa':
                self.do_media_pause()

            elif cmd == 'seek':
                self.do_seek_media(cmd_arg)

            elif cmd == 'cm':
                self.do_close_media()

            elif cmd == 'cpl':
                self.do_clear_playlist()

            elif cmd == 'yts':
                self._pool.add_task(self.do_youtube_search, cmd_arg)

            elif cmd == 'pyts':
                self.do_play_youtube_search(cmd_arg)

            elif cmd == 'lc':
                self.do_live_count(cmd_arg)

            elif cmd == 'lcw':
                self.do_live_count_watch_room(cmd_arg)

            elif cmd == 'lcr':
                self.do_remove_live_count_room(cmd_arg)

            elif cmd == 'lci':
                self.do_live_count_interval(cmd_arg)

            elif cmd == 'lcm':
                self.do_live_count_most_active()

            elif cmd == 'lcs':
                self.do_live_count_status()

            elif cmd == 'lcc':
                self.do_live_count_close()

            elif cmd == 'cv':
                self.do_vote_cancel()  # new

        if self._user.level <= UserLevel.BOT_OP:

            if cmd == 'spl':
                self.do_playlist_info(cmd_arg)

            elif cmd == 'clr':
                self.do_clear()

            elif cmd == 'nick':
                self.do_nick(cmd_arg)

            elif cmd == 'kick':
                self._pool.add_task(self.do_kick, cmd_arg)

            elif cmd == 'ban':
                self._pool.add_task(self.do_ban, cmd_arg)

            elif cmd == 'bn':
                self.do_bad_nick(cmd_arg)

            elif cmd == 'rmbn':
                self.do_remove_bad_nick(cmd_arg)

            elif cmd == 'bs':
                self.do_bad_string(cmd_arg)

            elif cmd == 'rmbs':
                self.do_remove_bad_string(cmd_arg)

            elif cmd == 'ba':
                self.do_bad_account(cmd_arg)

            elif cmd == 'rmba':
                self.do_remove_bad_account(cmd_arg)

            elif cmd == 'list':
                self.do_list_info(cmd_arg)

            elif cmd == 'uinfo':
                self.do_user_info(cmd_arg)

            elif cmd == 'cam':
                self.do_cam_approve(cmd_arg)

            elif cmd == 'cbc':
                self.do_broadcast(cmd_arg)

            elif cmd == 'is':
                self._pool.add_task(self.do_instagram_search, cmd_arg)

            elif cmd == 'porn':
                self._pool.add_task(self.do_porn_search, cmd_arg)

            elif cmd == 'close':
                self.do_close_broadcast(cmd_arg)

            elif cmd == 'sbl':
                self.do_banlist_search(cmd_arg)

            elif cmd == 'fg':
                self.do_forgive(cmd_arg)

            elif cmd == 'unb':
                self.do_unban(cmd_arg)

            elif cmd == 'jcd':
                self._pool.add_task(self.do_jc_directory)

            elif cmd == 'jcr':
                self._pool.add_task(self.do_jc_room_info, cmd_arg)

            elif cmd == 'jcu':
                self._pool.add_task(self.do_jc_user_search, cmd_arg)

        if (self._conf.PUBLIC_CMD and self._user.level <= UserLevel.DEFAULT) \
                or self._user.level < UserLevel.DEFAULT:

            if cmd == 'pmme':
                self.do_pmme()

            elif cmd == 'opme':
                self.do_opme(cmd_arg)

            elif cmd == 'v':
                self.do_version()

            elif cmd == 'help':
                self.do_help()

            elif cmd == 't':
                self.do_uptime()

            elif cmd == 'yt':
                self._pool.add_task(self.do_play_youtube, cmd_arg)

            elif cmd == 'q':
                self.do_playlist_status()

            elif cmd == 'n':
                self.do_next_tune_in_playlist()

            elif cmd == 'np':
                self.do_now_playing()

            elif cmd == 'wp':
                self.do_who_plays()

            # Tinychat API commands.
            elif cmd == 'acspy':
                self._pool.add_task(self.do_account_spy, cmd_arg)

            # Other API commands.
            elif cmd == 'urb':
                self._pool.add_task(self.do_search_urban_dictionary, cmd_arg)

            elif cmd == 'wea':
                self._pool.add_task(self.do_weather_search, cmd_arg)

            elif cmd == 'ip':
                self._pool.add_task(self.do_whois_ip, cmd_arg)

            elif cmd == 'wiki':
                self._pool.add_task(self.do_wiki, cmd_arg)

            # Just for fun.
            elif cmd == 'cn':
                self._pool.add_task(self.do_chuck_noris)

            elif cmd == '8ball':
                self.do_8ball(cmd_arg)

            elif cmd == 'roll':
                self.do_dice()

            elif cmd == 'flip':
                self.do_flip_coin()

        if self._conf.ENABLE_VOTING:

            # Voting
            if cmd == 'vtb':
                self.do_vote_session(cmd_arg, 'ban')  # new

            elif cmd == 'vtk':
                self.do_vote_session(cmd_arg, 'kick')  # new

            elif cmd == 'vtc':
                self.do_vote_session(cmd_arg, 'close')  # new

            elif cmd == 'vote':
                self.do_vote(cmd_arg)  # new

    # OWNER Command Methods.
    def do_make_mod(self, account):
        """
        Make a tinychat account a room moderator.

        :param account: The account to make a moderator.
        :type account: str
        """
        if len(account) == 0:
            self._responder('Missing account')
        else:
            tc_user = self._bot.privacy.make_moderator(account)
            if tc_user is None:
                self._responder('The account is invalid.')
            elif not tc_user:
                self._responder('%s is already a moderator.' % account)
            elif tc_user:
                self._responder('%s was made a room moderator.' % account)

    def do_remove_mod(self, account):
        """
        Removes a tinychat account from the moderator list.

        :param account: The account to remove from the moderator list.
        :type account: str
        """
        if len(account) == 0:
            self._responder('Missing account')
        else:
            tc_user = self._bot.privacy.remove_moderator(account)
            if tc_user:
                self._responder('%s is no longer a room moderator.' % account)

            elif not tc_user:
                self._responder('%s is not a room moderator.' % account)

    def do_directory(self):
        """
        Toggles if the room should be shown on the directory.
        """
        if self._bot.privacy.show_on_directory():
            self._responder('Room IS shown on the directory.')
        else:
            self._responder('Room is NOT shown on the directory.')

    def do_push2talk(self):
        """
        Toggles if the room should be in push2talk mode.
        """
        if self._bot.privacy.set_push2talk():
            self._responder('Push2Talk is enabled.')
        else:
            self._responder('Push2Talk is disabled.')

    def do_key(self, new_key):
        """
        Shows or sets a new secret bot controller key.

        :param new_key: The new secret key.
        :type new_key: str
        """
        if self._msg.type == 1:
            self._responder('Command only supported in PM.')
        else:
            if len(new_key) == 0:
                self._responder('The current secret key is: %s' %
                                self._conf.KEY)
            elif len(new_key) < 6:
                self._responder('The key is to short, it must be '
                                'at least 6 characters long. It is %s long.' %
                                len(new_key))
            elif len(new_key) >= 6:
                # reset current bot controllers in the room
                for user in self._bot.users.all:
                    user_level = self._bot.users.all[user].level
                    if user_level == UserLevel.SUPER or user_level == UserLevel.BOT_OP:
                        self._bot.users.all[user].level = UserLevel.DEFAULT

            self._conf.KEY = new_key
            self._responder('The key was changed to: %s' % new_key)

    def do_clear_bad_nicks(self):
        """
        Clear the nick bans file.
        """
        self._conf.NICK_BANS[:] = []
        file_handler.delete_file_content(self._bot.config_path,
                                         self._conf.NICK_BANS_FILE_NAME)
        self._responder('Nick file cleared.')

    def do_clear_bad_strings(self):
        """
        Clear the string bans file.
        """
        self._conf.STRING_BANS[:] = []
        file_handler.delete_file_content(self._bot.config_path,
                                         self._conf.STRING_BANS_FILE_NAME)
        self._responder('String file cleared.')

    def do_clear_bad_accounts(self):
        """
        Clear the account bans file.
        """
        self._conf.ACCOUNT_BANS[:] = []
        file_handler.delete_file_content(self._bot.config_path,
                                         self._conf.ACCOUNT_BANS_FILE_NAME)
        self._responder('Account file cleared.')

    def do_clear_approved_users(self):
        """
        Clear the approved file.
        """
        self._conf.APPROVED[:] = []
        file_handler.delete_file_content(self._bot.config_path,
                                         self._conf.APPROVED_FILE_NAME)
        self._responder('Approved file cleared.')

        # reset current approved users in the room
        for user in self._bot.users.all:
            if self._bot.users.all[user].level == UserLevel.APPROVED:
                self._bot.users.all[user].level = UserLevel.DEFAULT

    def do_green_room(self):
        """
        Toggles if the room should be in greenroom mode.
        """
        if self._bot.privacy.set_greenroom():
            self._responder('Green room is enabled.')
        else:
            self._responder('Green room is disabled.')

    def do_kill(self):
        """
        Kills the bot.
        """
        self._bot.disconnect()

    def do_reboot(self):
        """
        Reboots the bot.
        """
        self._bot.reconnect()

    # SUPER Command Methods.
    def do_media_info(self):
        """
        Show information about the currently playing youtube.
        """
        if self._playlist.has_active_track:
            self._responder(
                'Playlist Tracks: ' + str(len(self._playlist.track_list)) + '\n' +
                'Track Title: ' + self._playlist.track.title + '\n' +
                'Track Index: ' + str(self._playlist.track_index) + '\n' +
                'Elapsed Track Time: ' + self._bot.format_time(self._playlist.elapsed) + '\n' +
                'Remaining Track Time: ' + self._bot.format_time(self._playlist.remaining))
        else:
            self._responder('No media info available.')

    def do_dev(self):
        # TODO: Implement something here..
        pass

    # MODERATOR Command Methods.
    def do_op_user(self, user_name):
        """
        Lets the room owner or a mod
        make another user a bot controller.

        :param user_name: The user to op.
        :type user_name: str
        """
        if len(user_name) == 0:
            self._responder('Missing username.')
        else:
            user = self._bot.users.search_by_nick(user_name)
            if user is not None:
                # do not set user level for owner and moderators
                if not user.is_owner or not user.is_mod:
                    user.level = UserLevel.BOT_OP
                    self._responder('%s is now a bot controller' % user_name)
            else:
                self._responder('No user named: %s' % user_name)

    def do_deop_user(self, user_name):
        """
        Lets the room owner or a mod
        remove a user from being a bot controller.

        :param user_name: The user to deop.
        :type user_name: str
        """
        if len(user_name) == 0:
            self._responder('Missing username.')
        else:
            user = self._bot.users.search_by_nick(user_name)
            if user is not None:
                # do not set user level for owner and moderators
                if not user.is_owner or not user.is_mod:
                    user.level = UserLevel.DEFAULT
                    self._responder(
                        '%s is not a bot controller anymore.' % user_name)
            else:
                self._responder('No user named: %s' % user_name)

    def do_approve(self, username):
        """
        Add a user to the approved file.

        TODO: maybe add the ability to add of line user accounts?

        :param username: The user name of the user to add to the file.
        :type username: str
        """
        if len(username) == 0:
            self._responder('Missing user name.')
        else:
            user = self._bot.users.search_by_nick(username)
            if user is not None:
                if user.account is None:
                    self._responder('%s is not signed in.' % username)
                elif user.account in self._conf.APPROVED:
                    self._responder('%s is already approved.' % username)
                elif user.account != self._bot.account:
                    file_handler.writer(self._bot.config_path,
                                        self._conf.APPROVED_FILE_NAME, user.account)
                    self._responder('%s was added to file.' % user.account)
                    # do not set user level for owner and moderators
                    if not user.is_owner or not user.is_mod:
                        self._bot.users.mark_as_approved(user.handle)
                    self._bot.get_list(approved=True)

    def do_de_approve(self, account):
        """
        Remove an account from the approved file.

        :param account: The account name to remove from the file.
        :type account: str
        """
        if len(account) == 0:
            self._responder('Missing account name.')
        else:
            if account not in self._conf.APPROVED:
                self._responder('%s is not an approved account.' % account)
            elif account in self._conf.APPROVED:
                rem = file_handler.remove_from_file(self._bot.config_path,
                                                    self._conf.APPROVED_FILE_NAME,
                                                    account)
                if rem:
                    self._responder('%s was removed.' % account)
                    # check if there currently is
                    # a user in the room with this account
                    user = self._bot.users.search_by_account(account)
                    if user is not None:
                        # do not set user level for owner and moderators
                        if not user.is_owner or not user.is_mod:
                            # reset the user back to DEFAULT level
                            user.level = UserLevel.DEFAULT

                    self._bot.get_list(approved=True)

    def do_banned_by(self, moderator=''):
        """
        Count users banned by a specific moderator.

        :param moderator: The moderator to count banned users for.
        :type moderator: str
        """
        if len(moderator.strip()) == 0:
            moderator = self._bot.account

        banned_users = self._bot.users.search_banlist_by_moderator(moderator)

        if len(banned_users) == 0:
            self._responder('No users banned by: %s' % moderator)

        # could show the users, for now just count.
        elif len(banned_users) > 0:
            self._responder('%s user(s) have been banned by: %s' %
                            (len(banned_users), moderator))

    def do_guests(self):
        """
        Toggles if guests are allowed to join the room or not.
        """
        self._conf.ALLOW_GUESTS = not self._conf.ALLOW_GUESTS
        self._responder('Allow Guests: %s' % self._conf.ALLOW_GUESTS)

    def do_lurkers(self):
        """
        Toggles if lurkers are allowed or not.
        """
        self._conf.ALLOW_LURKERS = not self._conf.ALLOW_LURKERS
        self._responder('Allow Lurkers: %s' % self._conf.ALLOW_GUESTS)

    def do_guest_nicks(self):
        """
        Toggles if guest nicks are allowed or not.
        """
        self._conf.ALLOW_GUESTS_NICKS = not self._conf.ALLOW_GUESTS_NICKS
        self._responder('Allow Guest Nicks: %s' %
                        self._conf.ALLOW_GUESTS_NICKS)

    def do_greet(self):
        """ Toggles if users should be greeted on entry. """
        self._conf.GREET = not self._conf.GREET
        self._responder('Greet Users: %s' % self._conf.GREET)

    def do_public_cmds(self):
        """
        Toggles if public commands are public or not.
        """
        self._conf.PUBLIC_CMD = not self._conf.PUBLIC_CMD
        self._responder('Public Commands Enabled: %s' % self._conf.PUBLIC_CMD)

    def do_kick_as_ban(self):
        """
        Toggles if kick should be used instead of ban for auto bans .
        """
        self._conf.USE_KICK_AS_AUTOBAN = not self._conf.USE_KICK_AS_AUTOBAN
        self._responder('Use Kick As Auto Ban: %s' %
                        self._conf.USE_KICK_AS_AUTOBAN)

    def do_notify_on_ban(self):
        """
        Toggle if notify on ban should be enabled.
        """
        self._conf.NOTIFY_ON_BAN = not self._conf.NOTIFY_ON_BAN
        self._responder('Notify On Ban: %s' % self._conf.NOTIFY_ON_BAN)

    def do_vip_mode(self):
        """
        Toggle vip mode.
        """
        self._conf.VIP_MODE = not self._conf.VIP_MODE
        self._responder('Vip Mode: %s' % self._conf.VIP_MODE)

    def do_voting(self):
        """
        Enable/Disable voting.

        NOTE: If a voting session is active when
        disabling voting. Then that session will be cancelled.
        """
        self._conf.ENABLE_VOTING = not self._conf.ENABLE_VOTING

        if isinstance(self._bot.vote, Vote) and self._bot.vote.is_active:
            self.do_vote_cancel(True)
        else:
            self._responder('Voting Enabled: %s' % self._conf.ENABLE_VOTING)

    def do_room_settings(self):
        """
        Shows current room settings.
        """
        if self._bot.users.client.is_owner:
            settings = self._bot.privacy.current_settings()
            self._responder(
                'Broadcast Password: %s, \n '
                'Room Password: %s, \n '
                'Login Type: %s, \n '
                'Directory: %s, \n '
                'Push2Talk: %s, \n '
                'Greenroom: %s' %
                (settings['broadcast_pass'],
                 settings['room_pass'],
                 settings['allow_guest'],
                 settings['show_on_directory'],
                 settings['push2talk'],
                 settings['greenroom']))
        else:
            self._responder('Not using room owner account.')

    def do_lastfm_chart(self, chart_items):
        """
        Create a playlist from the most played tracks on last.fm.

        :param chart_items: The maximum amount of chart items.
        :type chart_items: str | int
        """
        if chart_items is None or len(chart_items) == 0:
            self._responder('Please specify the max amount of tracks.')
        else:
            try:
                chart_items = int(chart_items)
            except ValueError:
                self._responder('Only numbers allowed.')
            else:
                if 0 < chart_items <= 30:
                    self._responder('Creating a playlist...')
                    _items = lastfm.chart(chart_items)
                    if _items is not None:
                        self._playlist.add_list(self._user.nick, _items)
                        self._responder('Added %s tracks from last.fm chart' %
                                        len(_items))

                        if not self._playlist.has_active_track:
                            track = self._playlist.next_track
                            self._bot.send_yut_play(
                                track.id, track.time, track.title)
                            self._bot.timer.start(
                                self._bot.timer_event, track.time)
                    else:
                        self._responder(
                            'Failed to retrieve a result from last.fm.')
                else:
                    self._responder('Max 30 tracks.')

    def do_lastfm_random_tunes(self, max_tracks):
        """
        Creates a playlist from what other people
        are listening to on last.fm

        :param max_tracks: The maximum amount of tracks.
        :type max_tracks: str | int
        """
        if len(max_tracks) == 0 or max_tracks is None:
            self._responder('Please specify the max amount of tracks.')
        else:
            try:
                max_tracks = int(max_tracks)
            except ValueError:
                self._responder('Only numbers allowed.')
            else:
                if 0 < max_tracks < 50:
                    self._responder('Creating playlist...')
                    _items = lastfm.listening_now(max_tracks)
                    if _items is not None:
                        self._playlist.add_list(self._user.nick, _items)
                        self._responder(
                            'Added %s tracks from last.fm' % len(_items))

                        if not self._playlist.has_active_track:
                            track = self._playlist.next_track
                            self._bot.send_yut_play(
                                track.id, track.time, track.title)
                            self._bot.timer.start(
                                self._bot.timer_event, track.time)
                    else:
                        self._responder(
                            'Failed to retrieve a result from last.fm.')
                else:
                    self._responder('Max 50 tracks.')

    def do_search_lastfm_by_tag(self, search_str):
        """
        Search last.fm for tunes matching a tag.

        :param search_str: The search tag to search for.
        :type search_str: str
        """
        if len(search_str) == 0 or search_str is None:
            self._responder('Missing search string.')
        else:
            self._responder('Creating playlist..')
            _items = lastfm.tag_search(search_str)
            if _items is not None:
                self._playlist.add_list(self._user.nick, _items)
                self._responder('Added %s tracks from last.fm' % len(_items))
                if not self._playlist.has_active_track:
                    track = self._playlist.next_track
                    self._bot.send_yut_play(track.id, track.time, track.title)
                    self._bot.timer.start(self._bot.timer_event, track.time)
            else:
                self._responder('Failed to retrieve a result from last.fm.')

    def do_youtube_playlist_search(self, search_str):
        """
        Search youtube for a playlist.

        :param search_str: The search term to search for.
        :type search_str: str
        """
        if len(search_str) == 0:
            self._responder('Missing search string.')
        else:
            self._bot.search_list = Youtube.playlist_search(search_str)
            if len(self._bot.search_list) > 0:
                self._bot.is_search_list_yt_playlist = True
                _ = []
                for i, pl in enumerate(self._bot.search_list):
                    playlist = '(%s) - %s' % (i, pl['playlist_title'])
                    _.append(playlist)

                self._responder('\n'.join(_))
            else:
                self._responder(
                    'Failed to find playlist matching search term: %s' % search_str)

    def do_play_youtube_playlist(self, int_choice):
        """
        Play a previous searched playlist.

        :param int_choice: The index of the playlist.
        :type int_choice: str | int
        """
        if self._bot.is_search_list_yt_playlist:
            try:
                int_choice = int(int_choice)
            except ValueError:
                self._responder('Only numbers allowed.')
            else:
                if 0 <= int_choice <= len(self._bot.search_list) - 1:
                    self._responder('Creating playlist..')
                    playlist_id = self._bot.search_list[int_choice]['playlist_id']
                    tracks = Youtube.id_details(playlist_id, True)
                    if len(tracks) > 0:
                        self._playlist.add_list(self._user.nick, tracks)
                        self._responder(
                            'Added %s tracks from youtube playlist.' % len(tracks))
                        if not self._playlist.has_active_track:
                            track = self._playlist.next_track
                            self._bot.send_yut_play(
                                track.id, track.time, track.title)
                            self._bot.timer.start(
                                self._bot.timer_event, track.time)
                    else:
                        self._responder(
                            'Failed to retrieve videos from youtube playlist.')
                else:
                    max_ = len(self._bot.search_list) - 1
                    self._responder('Please make a choice between 0-%s' % max_)
        else:
            self._responder(
                'The search list does not contain any youtube playlist id\'s.')

    def do_show_search_list(self):
        """
        Show what the search list contains.
        """
        if len(self._bot.search_list) == 0:
            self._responder('The search list is empty.')
        else:
            _ = []
            if self._bot.is_search_list_yt_playlist:

                for i, pl in enumerate(self._bot.seaech_list):
                    pl_data = '(%s) - %s' % (i, pl['playlist_title'])
                    _.append(pl_data)
                self._responder('Youtube Playlist\'s\n'.join(_))
            else:

                for i, t in enumerate(self._bot.search_list):
                    track_data = '(%s) %s %s' % (
                        i, t['video_title'], t['video_time'])
                    _.append(track_data)
                self._responder('Youtube Tracks\n'.join(_))

    # APPROVED Command Methods.
    def do_skip(self):
        """
        Skip to the next item in the playlist.
        """
        if self._playlist.is_last_track is None:
            self._responder('No tunes to skip. The playlist is empty.')
        elif self._playlist.is_last_track:
            self._responder('This is the last track in the playlist.')
        else:
            self._bot.timer.cancel()
            next_track = self._playlist.next_track
            self._bot.send_yut_play(
                next_track.id, next_track.time, next_track.title)
            self._bot.timer.start(self._bot.timer_event, next_track.time)

    def do_delete_playlist_item(self, to_delete):
        """
        Delete items from the playlist.

        TODO: Make sure this is working.

        :param to_delete: Item indexes to delete.
        :type to_delete: str
        """
        if len(self._playlist.track_list) == 0:
            self._responder('The playlist is empty.')
        elif len(to_delete) == 0:
            self._responder('No indexes provided.')
        else:
            indexes = None
            by_range = False

            try:
                if ':' in to_delete:
                    range_indexes = map(int, to_delete.split(':'))
                    temp_indexes = range(
                        range_indexes[0], range_indexes[1] + 1)
                    if len(temp_indexes) > 1:
                        by_range = True
                else:
                    temp_indexes = map(int, to_delete.split(','))
            except ValueError as ve:
                log.error('wrong format: %s' % ve)
            else:
                indexes = []
                for i in temp_indexes:
                    if i < len(self._playlist.track_list) and i not in indexes:
                        indexes.append(i)

            if indexes is not None and len(indexes) > 0:
                result = self._playlist.delete(indexes, by_range)
                if result is not None:
                    if by_range:
                        self._responder('Deleted from index: %s to index: %s' %
                                        (result['from'], result['to']))
                    elif result['deleted_indexes_len'] == 1:
                        self._responder('Deleted %s' % result['track_title'])
                    else:
                        self._responder('Deleted tracks at index: %s' %
                                        ', '.join(result['deleted_indexes']))
                else:
                    self._responder('Nothing was deleted.')

    def do_media_replay(self):
        """
        Replay the currently playing track.
        """
        if self._playlist.track is not None:
            self._bot.timer.cancel()
            track = self._playlist.replay()
            self._bot.send_yut_play(track.id, track.time, track.title)
            self._bot.timer.start(self._bot.timer_event, track.time)

    def do_play_media(self):
        """
        Play a track on pause.
        """
        if self._playlist.track is not None:
            if self._playlist.has_active_track:
                self._bot.timer.cancel()
            if self._playlist.is_paused:
                self._playlist.play(self._playlist.elapsed)
                self._bot.send_yut_play(self._playlist.track.id, self._playlist.track.time,
                                        self._playlist.track.title, self._playlist.elapsed)  #
                self._bot.timer.start(
                    self._bot.timer_event, self._playlist.remaining)

    def do_media_pause(self):
        """
        Pause a track.
        """
        track = self._playlist.track
        if track is not None:
            if self._playlist.has_active_track:
                self._bot.timer.cancel()
            self._playlist.pause()
            self._bot.send_yut_pause(
                track.id, track.time, self._playlist.elapsed)

    def do_close_media(self):
        """
        Close a track playing.
        """
        if self._playlist.has_active_track:
            self._bot.timer.cancel()
            self._playlist.stop()
            self._bot.send_yut_stop(self._playlist.track.id,
                                    self._playlist.track.time,
                                    offset=self._playlist.elapsed)

    def do_seek_media(self, time_point):
        """
        Time search a track.

        :param time_point: The time point in which to search to.
        :type time_point: str
        """
        if ('h' in time_point) or ('m' in time_point) or ('s' in time_point):
            offset = string_util.convert_to_seconds(time_point)
            if offset == 0:
                self._responder('Invalid seek time.')
            else:
                track = self._playlist.track
                if track is not None:
                    if 0 < offset < track.time:
                        if self._playlist.has_active_track:
                            self._bot.timer.cancel()
                        if self._playlist.is_paused:
                            self._playlist.pause(offset=offset)  #
                            self._bot.send_yut_pause(
                                track.id, track.time, offset)
                        else:
                            self._playlist.play(offset)
                            self._bot.send_yut_play(
                                track.id, track.time, track.title, offset)
                            self._bot.timer.start(
                                self._bot.timer_event, self._playlist.remaining)

    def do_clear_playlist(self):
        """
        Clear the playlist for items.
        """
        if len(self._playlist.track_list) > 0:
            pl_length = len(self._playlist.track_list)
            self._playlist.clear()
            self._responder('Deleted %s items in the playlist.' % pl_length)
        else:
            self._responder('The playlist is empty, nothing to delete.')

    def do_playlist_info(self, amount=3):
        """
        Shows the next tracks in the playlist.
        """
        if len(self._playlist.track_list) > 0:
            try:
                amount = int(amount)
            except ValueError:
                amount = 3

            tracks = self._playlist.get_tracks(amount=amount)
            if len(tracks) > 0:
                _ = []
                for i, t in enumerate(tracks):
                    if i == 0:
                        info = 'Next track (%s) - %s %s' % \
                               (t[0], t[1].title, self._bot.format_time(t[1].time))
                    else:
                        info = '(%s) - %s %s' % \
                               (t[0], t[1].title, self._bot.format_time(t[1].time))
                    _.append(info)

                msg = '\n'.join(_)
                if len(msg) < 450:
                    self._responder(msg)
                else:
                    self._responder('To many items in playlist to show.')

    def do_youtube_search(self, search_str):
        """
        Search youtube for a list of matching candidates.

        :param search_str: The search term to search for.
        :type search_str: str
        """
        if len(search_str) == 0:
            self._responder('Missing search string.')
        else:
            self._bot.search_list = Youtube.search(search_str, results=5)
            if len(self._bot.search_list) > 0:
                self._bot.is_search_list_yt_playlist = False
                _ = []
                for i, t in enumerate(self._bot.search_list):
                    info = '(%s) %s %s' % (
                        i, t.title, self._bot.format_time(t.time))
                    _.append(info)
                self._responder('\n'.join(_))
            else:
                self._responder(
                    'Could not find anything matching: %s' % search_str)

    def do_play_youtube_search(self, int_choice):
        """
        Play a track from a previous youtube search list.

        :param int_choice: The index of the track in the search.
        :type int_choice: str | int
        """
        if not self._bot.is_search_list_yt_playlist:
            if len(self._bot.search_list) > 0:
                try:
                    int_choice = int(int_choice)
                except ValueError:
                    self._responder('Only numbers allowed.')
                else:
                    if 0 <= int_choice <= len(self._bot.search_list) - 1:

                        if self._playlist.has_active_track:
                            track = self._playlist.add(self._user.nick,
                                                       self._bot.search_list[int_choice])
                            self._responder('Added (%s) %s %s' %
                                            (self._playlist.last_index,
                                             track.title, self._bot.format_time(track.time)))
                        else:
                            track = self._playlist.start(self._user.nick,
                                                         self._bot.search_list[int_choice])
                            self._bot.send_yut_play(
                                track.id, track.time, track.title)
                            self._bot.timer.start(
                                self._bot.timer_event, track.time)
                    else:
                        max_ = len(self._bot.search_list) - 1
                        self._responder(
                            'Please make a choice between 0-%s' % max_)
            else:
                self._responder('No youtube track id\'s in the search list.')
        else:
            self._responder(
                'The search list only contains youtube playlist id\'s.')

    def do_live_count(self, watch_room):  # TODO: TEST
        """
        Start live count.

        :param watch_room: The room to watch for live count.
        :type watch_room: str | None
        """
        if self._msg.type == 2:
            self._responder('Not supported in PM.')
        else:
            # maybe use isinstance instead
            if self._bot.live_count is not None and self._bot.live_count.connected:
                self._responder('Live count already connected.')
            else:
                if len(watch_room) == 0:
                    self._bot.live_count = LiveCount(self._bot)
                else:
                    self._bot.live_count = LiveCount(self._bot, watch_room)
                # start live count thread
                thread_task(self._bot.live_count.connect)

    def do_live_count_watch_room(self, room_name):  # TODO: TEST
        """
        Set or change the live count room.

        :param room_name: The room name to watch .
        :type room_name: str
        """
        if self._bot.live_count is None:
            self._responder('Live count not connected.')
        elif len(room_name) == 0:
            self._responder('No watch room provided')
        else:
            self._bot.live_count.add_watch_room(room_name)

    def do_remove_live_count_room(self, room_name):
        """
        Remove a room name from the live count watch.

        :param room_name: The room name to remove.
        :type room_name: str
        """
        if self._bot.live_count is None:
            self._responder('Live count is not connected.')
        elif len(room_name) == 0:
            self._responder('No room name provided.')
        else:
            self._bot.live_count.remove_watch_room(room_name)

    def do_live_count_interval(self, interval):  # TODO: TEST
        """
        Set the live count interval.

        :param interval: The interval in seconds.
        :type interval: int
        """
        try:
            interval = int(interval)
        except ValueError:
            self._responder('int expected.')
        else:
            if self._bot.live_count is None:
                self._responder('Live count not connected.')
            else:
                self._bot.live_count.set_watch_interval(interval)

    def do_live_count_most_active(self):  # TODO: TEST
        """
        The most active in room in the live count.
        """
        if self._bot.live_count is None:
            self._responder('Live count not connected.')
        else:
            self._bot.live_count.most_active()

    def do_live_count_status(self):
        """
        Live count status.
        """
        if self._bot.live_count is None:
            self._responder('Live count not connected.')
        else:
            self._bot.live_count.status()

    def do_live_count_close(self):
        """
        Close the live count.
        """
        if self._bot.live_count is None:
            self._responder('Live count not connected.')
        else:
            self._bot.live_count.disconnect()
            self._bot.live_count = None

    def do_vote_cancel(self, disable=False):
        """
        Cancel a vote session.

        :param disable:
        :type disable: bool
        """
        if self._msg.type == 2:
            self._responder('Not supported in PM.')
        else:
            if isinstance(self._bot.vote, Vote) and self._bot.vote.is_active:
                if self._bot.vote.cancel():
                    if disable:
                        self._responder('Voting Enabled: %s' % self._conf.ENABLE_VOTING)
                    else:
                        self._responder('%s cancelled vote to %s %s' %
                                        (self._user.nick, self._bot.vote.active_vote_type,
                                         self._bot.vote.vote_user.nick))

                    self._bot.vote = None

    # BOT_OP Command Methods.
    def do_clear(self):
        """
        Clears the chat box.
        """
        self._responder('_{:\n^60}_'.format(''))

    def do_nick(self, new_nick):
        """
        Set a new nick for the bot.

        :param new_nick: The new nick name.
        :type new_nick: str
        """
        if len(new_nick) == 0:
            self._bot.nick = string_util.create_random_string(5, 25)
            self._bot.set_nick()
        else:
            self._bot.nick = new_nick
            pat = '^[a-zA-Z0-9_]{1,32}$'
            if not string_util.is_valid_string(self._bot.nick, pattern=pat):
                self._responder('Nick name may only contain a-zA-z0-9_')
            else:
                self._bot.set_nick()

    def do_kick(self, user_name):
        """
        Kick a user out of the room.

        :param user_name: The username to kick.
        :type user_name: str
        """
        if len(user_name) == 0:
            self._responder('Missing username.')
        elif user_name == self._bot.nick:
            self._responder('Action not allowed.')
        else:
            if user_name.startswith('*'):
                user_name = user_name.lstrip('*')
                _users = self._bot.users.search_containing(user_name)
                if len(_users) > 0:
                    for i, user in enumerate(_users):
                        if user.nick != self._bot.nick and user.level > self._user.level:
                            if i <= self._conf.MAX_MATCH_BANS - 1:
                                self._bot.send_kick_msg(user.handle)
            else:
                _user = self._bot.users.search_by_nick(user_name)
                if _user is None:
                    self._responder('No user named: %s' % user_name)
                elif _user.level < self._user.level:
                    self._responder('Not allowed.')
                else:
                    self._bot.send_kick_msg(_user.handle)

    def do_ban(self, user_name):
        """
        Ban a user from the room.

        :param user_name: The username to ban.
        :type user_name: str
        """
        if len(user_name) == 0:
            self._responder('Missing username.')
        elif user_name == self._bot.nick:
            self._responder('Action not allowed.')
        else:
            if user_name.startswith('*'):
                user_name = user_name.lstrip('*')
                _users = self._bot.users.search_containing(user_name)
                if len(_users) > 0:
                    for i, user in enumerate(_users):
                        if user.nick != self._bot.nick and user.level > self._user.level:
                            if i <= self._conf.MAX_MATCH_BANS - 1:
                                self._bot.send_ban_msg(user.handle)
            else:
                _user = self._bot.users.search_by_nick(user_name)
                if _user is None:
                    self._responder('No user named: %s' % user_name)
                elif _user.level < self._user.level:
                    self._responder('Not allowed.')
                else:
                    self._bot.send_ban_msg(_user.handle)

    def do_bad_nick(self, bad_nick):
        """
        Adds a username to the nick bans file.

        :param bad_nick: The bad nick to write to the nick bans file.
        :type bad_nick: str
        """
        if len(bad_nick) == 0:
            self._responder('Missing username.')
        elif bad_nick in self._conf.NICK_BANS:
            self._responder('%s is already in list.' % bad_nick)
        elif not string_util.is_valid_string(bad_nick,
                                             pattern='^[a-zA-Z0-9_*]{1,32}$'):
            self._responder('the nick provided is not valid.')
        else:
            file_handler.writer(self._bot.config_path,
                                self._conf.NICK_BANS_FILE_NAME, bad_nick)
            self._responder('%s was added to file.' % bad_nick)
            self._bot.get_list(nicks=True)

    def do_remove_bad_nick(self, bad_nick):
        """
        Removes nick from the nick bans file.

        :param bad_nick: The bad nick to remove from the nick bans file.
        :type bad_nick: str
        """
        if len(bad_nick) == 0:
            self._responder('Missing username')
        else:
            if bad_nick in self._conf.NICK_BANS:
                rem = file_handler.remove_from_file(self._bot.config_path,
                                                    self._conf.NICK_BANS_FILE_NAME,
                                                    bad_nick)
                if rem:
                    self._responder('%s was removed.' % bad_nick)
                    self._bot.get_list(nicks=True)

    def do_bad_string(self, bad_string):
        """
        Adds a string to the string bans file.

        :param bad_string: The bad string to add to the string bans file.
        :type bad_string: str
        """
        if len(bad_string) == 0:
            self._responder('Ban string can\'t be blank.')
        elif len(bad_string) < 3:
            self._responder('Ban string to short: %s' % len(bad_string))
        elif bad_string in self._conf.STRING_BANS:
            self._responder('%s is already in list.' % bad_string)
        else:
            file_handler.writer(self._bot.config_path,
                                self._conf.STRING_BANS_FILE_NAME, bad_string)
            self._responder('%s was added to file.' % bad_string)
            self._bot.get_list(strings=True)

    def do_remove_bad_string(self, bad_string):
        """
        Removes a string from the string bans file.

        :param bad_string: The bad string to remove from the string bans file.
        :type bad_string: str
        """
        if len(bad_string) == 0:
            self._responder('Missing word string.')
        else:
            if bad_string in self._conf.STRING_BANS:
                rem = file_handler.remove_from_file(self._bot.config_path,
                                                    self._conf.STRING_BANS_FILE_NAME,
                                                    bad_string)
                if rem:
                    self._responder('%s was removed.' % bad_string)
                    self._bot.get_list(strings=True)

    def do_bad_account(self, account):
        """
        Adds an account name to the account bans file.

        :param account: The bad account name to add to the account bans file.
        :type account: str
        """
        if len(account) == 0:
            self._responder('Account can\'t be blank.')
        elif account in self._conf.ACCOUNT_BANS:
            self._responder('%s is already in list.' % account)
            # apparently facebook names can cause an issue here(CosmosisT)
        elif not string_util.is_valid_string(account, '^[a-zA-Z0-9]{1,64}$'):
            self._responder(
                'Account name may only be a-zA-Z0-9 with a length of max 64 characters.')
        else:
            file_handler.writer(self._bot.config_path,
                                self._conf.ACCOUNT_BANS_FILE_NAME,
                                account)
            self._responder('%s was added to file.' % account)
            self._bot.get_list(accounts=True)

    def do_remove_bad_account(self, bad_account):
        """
        Removes an account from the account bans file.

        :param bad_account: The bad account name to remove from account bans file.
        :type bad_account: str
        """
        if len(bad_account) == 0:
            self._responder('Missing account.')
        else:
            if bad_account in self._conf.ACCOUNT_BANS:
                rem = file_handler.remove_from_file(self._bot.config_path,
                                                    self._conf.ACCOUNT_BANS_FILE_NAME,
                                                    bad_account)
                if rem:
                    self._responder('%s was removed.' % bad_account)
                    self._bot.get_list(accounts=True)

    def do_list_info(self, list_type):
        """
        Counts items in lists/files.

        :param list_type: The type of list to count.
        :type list_type: str
        """
        if len(list_type) == 0:
            self._responder('Missing list type.')
        else:
            if list_type.lower() == 'ap':
                if len(self._conf.APPROVED) == 0:
                    self._responder('No items in this list.')
                else:
                    self._responder('%s approved accounts in list.' %
                                    len(self._conf.APPROVED))

            if list_type.lower() == 'bn':
                if len(self._conf.NICK_BANS) == 0:
                    self._responder('No items in this list.')
                else:
                    self._responder('%s nicks bans in list.' %
                                    len(self._conf.NICK_BANS))

            elif list_type.lower() == 'bs':
                if len(self._conf.STRING_BANS) == 0:
                    self._responder('No items in this list.')
                else:
                    self._responder('%s string bans in list.' %
                                    len(self._conf.STRING_BANS))

            elif list_type.lower() == 'ba':
                if len(self._conf.ACCOUNT_BANS) == 0:
                    self._responder('No items in this list.')
                else:
                    self._responder('%s account bans in list.' %
                                    len(self._conf.ACCOUNT_BANS))

            elif list_type.lower() == 'bl':
                if len(self._bot.users.banned_users) == 0:
                    self._responder('The banlist is empty.')
                else:
                    _ = []
                    for i, banned in enumerate(self._bot.users.banned_users):
                        ban_data = '(%s) %s:%s [%s]' % \
                                   (i, banned.nick, banned.account, banned.ban_id)
                        _.append(ban_data)
                    _bans = '\n'.join(_)
                    if len(_bans) > 450:
                        # maybe have a MAX_MSG_LENGTH in config
                        # use string_util.chunk_string
                        self._responder('To many banned users to show.')
                    else:
                        self._responder(_bans)

            elif list_type.lower() == 'mods':
                if self._bot.users.client.is_owner:
                    if len(self._bot.privacy.room_moderators) == 0:
                        self._responder(
                            'There is currently no moderators for this room.')
                    elif len(self._bot.privacy.room_moderators) is not 0:
                        mods = ', '.join(self._bot.privacy.room_moderators)
                        self._responder('Moderators: %s' % mods)

    def do_user_info(self, user_name):
        """
        Shows user object info for a given user name.

        :param user_name: The user name of the user to show the info for.
        :type user_name: str
        """
        if len(user_name) == 0:
            self._responder('Missing username.')
        else:
            user = self._bot.users.search_by_nick(user_name)
            if user is None:
                self._responder('No user named: %s' % user_name)
            else:
                if user.role is None and user.account:
                    user_info = TinychatApi.user_info(user.account)
                    if user_info is not None:
                        user.biography = user_info['biography']
                        user.gender = user_info['gender']
                        user.age = user_info['age']
                        user.location = user_info['location']
                        user.role = user_info['role']

                info = [
                    'User Level: %s' % user.level,
                    'Join Time: %s' % user.join_time,
                    'Last Message: %s' % user.last_msg
                ]
                if user.role is not None:
                    info.append('Role: %s' % user.role)
                    info.append('Age: %s' % user.age)
                    info.append('Gender: %s' % user.gender)
                    info.append('Location: %s' % user.location)
                    info.append('Biography %s' % user.biography)

                self._responder('\n'.join(info))

    def do_cam_approve(self, user_name):
        """
        Allow a user to broadcast in a green room enabled room.

        :param user_name: The name of the user allowed to broadcast.
        :type user_name: str
        """
        if self._bot.state.is_green_room:
            if len(user_name) == 0 and self._user.is_waiting:
                self._bot.send_cam_approve_msg(self._user.handle)
            elif len(user_name) > 0:
                user = self._bot.users.search_by_nick(user_name)
                if user is not None and user.is_waiting:
                    self._bot.send_cam_approve_msg(user.handle)
                else:
                    self._responder('No user named: %s' % user_name)

    def do_broadcast(self, username):
        """
        Toggle if a user is allowed to broadcast.

        :param username: The user name of the user.
        :type username: str
        """
        if len(username) == 0:
            self._responder('Missing username.')
        else:
            user = self._bot.users.search_by_nick(username)
            if user is not None:
                if self._user.level >= user.level:
                    user.can_broadcast = not user.can_broadcast
                    if user.can_broadcast:
                        self._responder(
                            '%s is allowed to broadcast.' % username)
                    else:
                        self._responder(
                            '%s is not allowed to broadcast.' % username)
            else:
                self._responder('No user named: %s' % username)

    def do_instagram_search(self, user):
        """
        Search instagram for a user.

        :param user: The instagram user to search for.
        :type user: str
        """
        if len(user) == 0:
            self._responder('Missing search query.')
        else:
            insta_users = other.instagram_search(user)
            if len(insta_users) > 0:
                _ = []
                for i, u in enumerate(insta_users):
                    d = '(%s) - %s - %s - %s' % \
                        (i, u['username'], u['byline'], u['url'])
                    _.append(d)

                self._responder('\n'.join(_))

    def do_porn_search(self, keyword):
        """
        Search for porn.

        :param keyword: The keyword the to search for.
        :type keyword: str
        """
        if len(keyword) == 0:
            self._responder('Missing search keyword.')
        else:
            videos = other.porn(keyword)
            if len(videos) > 0:
                self._responder('\n'.join(videos))
            else:
                self._responder('No `%s` porn found.' % keyword)

    def do_close_broadcast(self, user_name):
        """
        Close a users broadcast.

        :param user_name: The name of the user to close.
        :type user_name: str
        """
        if len(user_name) == 0:
            self._responder('Missing user name.')
        else:
            user = self._bot.users.search_by_nick(user_name)
            if user is not None and user.is_broadcasting:
                self._bot.send_close_user_msg(user.handle)
            else:
                self._responder('No user named: %s' % user_name)

    def do_banlist_search(self, user_name):
        """
        Search the banlist for matches.

        :param user_name: The user name or partial username to search for.
        :type user_name: str
        """
        if len(user_name) == 0:
            self._responder('Missing user name to search for.')
        else:
            self._bot.bl_search_list = self._bot.users.search_banlist_containing(
                user_name)
            if len(self._bot.bl_search_list) == 0:
                self._responder('No banlist matches.')
            else:
                ban_list_info = []
                for i, banned in enumerate(self._bot.bl_search_list):
                    banned_user = '(%s) %s:%s [%s]' % \
                                  (i, banned.nick, banned.account, banned.ban_id)
                    ban_list_info.append(banned_user)

                _ = '\n'.join(ban_list_info)
                if len(_) < 400:
                    self._responder(_)
                else:
                    self._responder('To many banlist items to show.')

    def do_forgive(self, user_index):
        """
        Forgive a user from the ban list search.

        :param user_index: The index in the ban list search.
        :type user_index: str | int
        """
        try:
            user_index = int(user_index)
        except ValueError:
            self._responder('Only numbers allowed (%s)' % user_index)
        else:
            if len(self._bot.bl_search_list) > 0:
                if user_index <= len(self._bot.bl_search_list) - 1:
                    self._bot.send_unban_msg(
                        self._bot.bl_search_list[user_index].ban_id)
                else:
                    if len(self._bot.bl_search_list) > 1:
                        max_ = len(self._bot.bl_search_list)
                        self._responder(
                            'Please make a choice between 0-%s' % max_)
            else:
                self._responder('The ban search is empty.')

        # self.bl_search_list[:] = []

    def do_unban(self, user_name):
        """
        Un-ban the last banned user or a user by user name.

        NOTE: experimental. In case the user name match more than one
        user in the banlist, then the last banned user will be unbanned.

        :param user_name: The exact user name to unban.
        :type user_name: str
        """
        if len(user_name.strip()) == 0:
            last_banned_user = self._bot.users.last_banned
            if last_banned_user is not None:
                self._bot.send_unban_msg(last_banned_user.ban_id)
                self._responder('Unbanned: %s' % last_banned_user.nick)
            else:
                self._responder('Failed to find the last banned user.')
        else:
            banned_user = self._bot.users.search_banlist_by_nick(user_name)
            if banned_user is not None:
                self._bot.send_unban_msg(banned_user.ban_id)
                self._responder('Unbanned: %s' % banned_user.nick)
            else:
                self._responder(
                    'No user named: %s in the banlist.' % user_name)

    def do_jc_directory(self):
        """
        Gets a status of the rooms and users using jumpin.chat
        """
        self._responder('Gathering information..')

        rooms = JumpinChatApi.directory()
        users = []

        if len(rooms) == 0:
            self._responder('No rooms on the directory.')

        else:
            for r in rooms:
                for u in r.users:
                    if u.nick not in users:
                        users.append(u.nick)

            self._responder('%s unique users in %s room(s) on jumpin.chat' %
                            (len(users), len(rooms)))

    def do_jc_room_info(self, room_name):
        """
        Get the room information for a room on jumpin.chat

        :param room_name: The room name to get the information for.
        :type room_name: str
        """
        if len(room_name) == 0:
            self._responder('Missing room name.')
        else:
            room = JumpinChatApi.room(room_name)
            if room is None:
                self._responder('%s is empty.' % room_name)
            else:
                broadcasters = []
                for user in room.users:
                    if user.is_broadcasting:
                        broadcasters.append(user)

                self._responder('%s, %s users, %s broadcasting' %
                                (room_name, len(room.users), len(broadcasters)))

    def do_jc_user_search(self, account):
        """
        Search jumpin.chat rooms for a user matching the account.

        :param account: The account to search for.
        :type account: str
        """
        if len(account) == 0:
            self._responder('Missing account name.')
        else:
            self._responder('Searching rooms...')
            rooms = JumpinChatApi.user_search(account)
            if len(rooms) == 0:
                self._responder('No user found with account `%s`.' % account)
            else:
                _ = []
                for room in rooms:
                    info = '%s was found in %s, users %s' % \
                           (account, room.name, len(room.users))
                    _.append(info)

                self._responder(', '.join(_))

    # DEFAULT Command Methods.
    def do_pmme(self):
        """
        Opens a PM session with the bot.
        """
        self._bot.responder('How can i help you %s?' % self._user.nick,
                            msg_type=2, user=self._user)

    def do_opme(self, key):
        """
        Make a user a bot controller if the correct key is provided.

        :param key: The secret bot controller key.
        :type key: str
        """
        if self._msg.type == 1:
            self._responder('Command only supported in PM.')
        else:
            if len(key) == 0:
                self._responder('Missing key.')
            elif key == self._conf.SUPER_KEY:
                if self._bot.users.client.is_owner:
                    self._user.level = UserLevel.OWNER
                    self._responder('You are now a super mod.')
                else:
                    self._responder(
                        'The client is not using the owner account.')
            elif key == self._conf.KEY:
                if self._bot.users.client.is_mod:
                    self._user.level = UserLevel.SUPER
                    self._responder('You are now a bot controller.')
                else:
                    self._responder('The client is not moderator.')
            else:
                self._responder('Wrong key.')

    def do_playlist_status(self):
        """
        Shows the playlist queue.
        """
        if len(self._playlist.track_list) == 0:
            self._responder('The playlist is empty.')
        else:
            queue = self._playlist.queue
            if queue is not None:
                self._responder('%s items in the playlist, %s still in queue.' %
                                (queue[0], queue[1]))

    def do_next_tune_in_playlist(self):
        """
        Shows the next track in the playlist.
        """
        if self._playlist.is_last_track is None:
            self._responder('The playlist is empty.')
        elif self._playlist.is_last_track:
            self._responder('This is the last track.')
        else:
            pos, next_track = self._playlist.next_track_info()
            if next_track is not None:
                self._responder('(%s) %s %s' %
                                (pos, next_track.title,
                                 self._bot.format_time(next_track.time)))

    def do_now_playing(self):
        """
        Shows what track is currently playing.
        """
        if self._playlist.has_active_track:
            track = self._playlist.track
            if len(self._playlist.track_list) > 0:
                self._responder('(%s) %s %s\n%s' %
                                (self._playlist.current_index, track.title,
                                 self._bot.format_time(track.time), track.link))
            else:
                self._responder('%s %s\n%s' % (track.title,
                                self._bot.format_time(track.time), track.link))
        else:
            self._responder('No track playing.')

    def do_who_plays(self):
        """
        Show who requested the currently playing track.
        """
        if self._playlist.has_active_track:
            track = self._playlist.track
            ago = self._bot.format_time(int(time.time() - track.rq_time))
            self._responder('%s requested this track %s ago.' %
                            (track.owner, ago))
        else:
            self._responder('No track playing.')

    def do_version(self):
        """
        Show version info.
        """
        self._responder('Nortbot v %s' % self._conf.BOT_VERSION)

    def do_help(self):
        """
        Posts a link to github readme/wiki or other page about the bot commands.
        """
        self._responder(
            'Help: https://github.com/nortxort/nortbot/blob/master/COMMANDS.md')

    def do_uptime(self):
        """
         Shows the bots uptime.
         """
        self._responder('Bot-Uptime: %s' %
                        self._bot.format_time(self._bot.up_time))

    def do_play_youtube(self, search_str):
        """
        Plays a youtube video matching the search term.

        :param search_str: The search term.
        :type search_str: str
        """
        log.info('%s is searching youtube: %s' %
                 (self._user.nick, search_str))

        if len(search_str) == 0:
            self._responder('Please specify youtube title or link.')
        else:
            youtube = Youtube.search(search_str)

            if youtube is None:
                log.warning('youtube request returned: %s' % youtube)
                self._responder('No video(s) found: %s' % search_str)

            elif not youtube.is_embeddable:
                self._responder('This track is not embeddable.')

            else:
                if isinstance(youtube, list) and len(youtube) > 1:
                    self._playlist.add_list(self._user.nick, youtube)
                    self._responder(
                        'Added %s tracks from youtube playlist.' % len(youtube))

                    if not self._playlist.has_active_track:
                        track = self._playlist.next_track
                        self._bot.send_yut_play(
                            track.id, track.time, track.title)
                        self._bot.timer.start(
                            self._bot.timer_event, track.time)
                else:
                    if self._playlist.has_active_track:
                        track = self._playlist.add(self._user.nick, youtube)
                        self._responder('(%s) %s %s' %
                                        (self._playlist.last_index,
                                         track.title,
                                         self._bot.format_time(track.time)))
                    else:
                        track = self._playlist.start(self._user.nick, youtube)
                        self._bot.send_yut_play(
                            track.id, track.time, track.title)
                        self._bot.timer.start(
                            self._bot.timer_event, track.time)

    # == Tinychat API Command Methods. ==
    def do_account_spy(self, account):
        """
        Shows info about a tinychat account.

        :param account: tinychat account.
        :type account: str
        """
        if len(account) == 0:
            self._responder('Missing username to search for.')
        else:
            tc_usr = TinychatApi.user_info(account)
            if tc_usr is None:
                self._responder(
                    'Could not find tinychat info for: %s' % account)
            else:
                account_info = [
                    'Age: %s' % tc_usr['age'],
                    'Gender: %s' % tc_usr['gender'],
                    'Role: %s' % tc_usr['role'],
                    'Location: %s' % tc_usr['location']
                ]
                self._responder('\n'.join(account_info))

    # == Other API Command Methods. ==
    def do_search_urban_dictionary(self, search_str):
        """
        Shows urbandictionary definition of search string.

        :param search_str: The search string to look up a definition for.
        :type search_str: str
        """
        if len(search_str) == 0:
            self._responder('Please specify something to look up.')
        else:
            urban = other.urbandictionary_search(search_str)
            if urban is None:
                self._responder(
                    'Could not find a definition for: %s' % search_str)
            else:
                if len(urban) > 200:
                    chunks = string_util.chunk_string(urban, 200)
                    for i in range(0, 2):
                        self._responder(chunks[i], timeout=2.0)
                else:
                    self._responder(urban)

    def do_weather_search(self, search_str):
        """
        Shows weather info for a given search string.

        :param search_str: The search string to find weather data for.
        :type search_str: str
        """
        if len(search_str) == 0:
            self._responder('Please specify a city to search for.')
        else:
            weather = other.weather_search(search_str)
            if weather is None:
                self._responder(
                    'Could not find weather data for: %s' % search_str)
            else:
                self._responder(weather)

    def do_whois_ip(self, ip_str):
        """
        Shows whois info for a given ip address or domain.

        :param ip_str: The ip address or domain to find info for.
        :type ip_str: str
        """
        if len(ip_str) == 0:
            self._responder('Please provide an IP address or domain.')
        else:
            whois = other.whois(ip_str)
            if whois is None:
                self._responder('No info found for: %s' % ip_str)
            else:
                self._responder(whois)

    def do_wiki(self, search_term):
        """
        Search wikipedia.

        :param search_term: The search term to search wikipedia for.
        :type search_term: str
        """
        if len(search_term.strip()) == 0:
            self._responder('Missing search term.')
        else:
            wiki = WikiPedia.search(search_term)

            if not wiki.has_data:
                self._responder('Could not find anything on wikipedia matching: %s' % search_term)
            else:
                self._responder('%s %s' % (wiki.summary, wiki.link))

    # == Just For Fun Command Methods. ==
    def do_chuck_noris(self):
        """
        Shows a chuck norris joke/quote.
        """
        chuck = other.chuck_norris()
        if chuck is not None:
            self._responder(chuck)

    def do_8ball(self, question):
        """
        Shows magic eight ball answer to a yes/no question.

        :param question: The yes/no question.
        :type question: str
        """
        if len(question) == 0:
            self._responder('Question.')
        else:
            self._responder('8Ball %s' % locals_.eight_ball())

    def do_dice(self):
        """
        roll the dice.
        """
        self._responder('The dice rolled: %s' % locals_.roll_dice())

    def do_flip_coin(self):
        """
        Flip a coin.
        """
        self._responder('The coin was: %s' % locals_.flip_coin())

    def do_vote_session(self, cmd_args, vote_type):
        """
        Start a voting session.

        :param cmd_args: A username and optionally a session time in seconds.
        :type cmd_args: str
        :param vote_type: The type of vote to start.
        :type vote_type: str
        """
        log.debug('vote session: %s, vote type: %s' % (cmd_args, vote_type))
        if self._msg.type == 2:
            # vote session can't be started from PM
            pass
        else:
            if len(cmd_args) == 0:
                self._responder('Missing required user nick.')
            else:

                if isinstance(self._bot.vote, Vote) and self._bot.vote.is_active:
                    self._responder('A vote to %s session is in progress.' %
                                    self._bot.vote.active_vote_type)
                else:
                    self._bot.vote = Vote(self._bot)
                    if self._bot.vote.can_start(self._user):
                        session = 60

                        args = cmd_args.split(' ')
                        if len(args) > 1:
                            try:
                                # use string_util to convert 5m or such to int(seconds)
                                session = int(args[1])
                            except ValueError:
                                return
                            else:
                                if not 60 <= session <= 600:
                                    self._responder('Vote session must be between 60 seconds and 10 minutes.')
                                    return

                        user = self._bot.users.search_by_nick(args[0])
                        if user is not None:

                            if vote_type in ['ban', 'kick'] and user.level <= UserLevel.MODERATOR:
                                self._responder('You can\'t vote to %s this user.' % vote_type)
                            else:
                                if self._bot.vote.start(user, session, vote_type):
                                    # maybe add session time to this msg
                                    self._responder('Vote to {0} has started.\n '
                                                    'Vote using {1}vote yes or {1}vote no'
                                                    .format(vote_type, self._conf.PREFIX))
                        else:
                            log.debug('no user named: %s' % args[0])
                            # self._responder('No user named: %s' % args[0])
                    else:
                        log.debug('%s is not allowed to start a vote session.' % self._user)
                        # self._responder('You are not allowed to start a vote session.')

    def do_vote(self, vote):
        """
        Cast a vote to the vote session.

        :param vote: The yes/no vote to cast to the vote session.
        :type vote: str
        """
        if isinstance(self._bot.vote, Vote) and self._bot.vote.is_active:
            if self._user.handle in self._bot.vote.has_voted:
                # if a user already has voted, don't do anything
                log.debug('%s already voted.' % self._user)
                pass
            else:
                vote = vote.strip()
                if vote == '':
                    # cant vote blank
                    log.debug('%s voted blank.' % self._user)
                    return

                if self._bot.vote.vote(self._user, vote):
                    # the user has voted successfully, respond in PM
                    log.debug('%s voted successfully' % self._user)
                    self._bot.responder('Your %s vote was accepted.' % vote, msg_type=2, user=self._user)

