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

from util import web, string_util


API_KEY = 'AIzaSyCPQe4gGZuyVQ78zdqf9O5iEyfVLPaRwZg'

# set to empty list to disable region restriction check.
ALLOWED_COUNTRIES = ['DK', 'US']

REFERER = 'https://tinychat.com'


log = logging.getLogger(__name__)


class Track:
    """
    Class representing a youtube video.
    """
    def __init__(self, video_id='', video_time=0, video_title='',
                 image='', owner=None, embeddable=True, video_type='youTube'):
        self.id = video_id
        self.time = video_time
        self.title = video_title
        self.image = image
        self.owner = owner
        self.is_embeddable = embeddable
        self.type = video_type
        self.link = 'https://youtu.be/%s' % video_id
        self.rq_time = time.time()
        self.start = 0
        self.pause = 0

    def __repr__(self):
        return '<%s id=%s, ' \
               'time=%s, title=%s, image=%s, ' \
               'owner=%s, type=%s, rq_time=%s, ' \
               'start=%s, pause=%s, embeddable=%s>' % \
               (self.__class__.__name__, self.id, self.time,
                self.title, self.image, self.owner, self.type,
                self.rq_time, self.start, self.pause, self.is_embeddable)


class Youtube(object):
    """
    Youtube API class containing methods for querying youtube's API.

    TODO: Implement max video time length
    """
    _search_url = 'https://www.googleapis.com/youtube/v3/search?' \
                  'type=video&key={0}&maxResults=50&q={1}&part=snippet'

    _playlist_search_url = 'https://www.googleapis.com/youtube/v3/search?' \
                           'type=playlist&key={0}&maxResults=50&q={1}&part=snippet'

    _playlist_items_url = 'https://www.googleapis.com/youtube/v3/playlistItems?' \
                          'key={0}&playlistId={1}&maxResults=50&part=snippet,id'

    _video_details_url = 'https://www.googleapis.com/youtube/v3/videos?' \
                         'id={1}&key={0}&part=contentDetails,snippet,status'

    @classmethod
    def search(cls, search_term, results=0):
        """
        Search youtube for a video matching the search term.

        This works in a couple of different ways.

            a) search for a youtube by a search term.
            b) search using a youtube url. The video id will be parsed from the url.
            c) search using a youtube playlist url. The video id will be parsed from the url.
            d) search for a list of results matching the search term.
            e) search using a youtube ID.

        In case of b), c)(single track) and e) no region restriction check will be done.

        In case of c) adding 1/True/true after a playlist url,
        will get the videos(max 50) from that playlist ID.
        Region restriction check will be done.

        Region restriction. If a video is NOT allowed in ONE of the
        countries in the ALLOWED_COUNTRIES, it will not be returned.
        If a video is blocked in ONE of the ALLOWED_COUNTRIES
        it will not be returned.

        The reason for this is, if you have a somewhat international room,
        you would want as many people to be able to see the youtube.
        You can set the ALLOWED_COUNTRIES to match the users of your room somewhat.
        A compromise have to be made here. If you add to many countries,
        then search results could become rather obscure. To few countries,
        and you might end up with some users not being able to see the youtube.

        For more about country codes see:
        https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
        the alpha-2 code colon.

        :param search_term: The search term to search for
        :type search_term: str
        :param results: This should be 0 if not using d).
        :type results: int
        :return: A Track object, a list of Track objects or None.
        :rtype: Track | list | None
        """
        if cls._is_youtube_id(search_term):
            return cls.id_details(search_term, is_youtube_id=True)

        elif cls._is_youtube_url(search_term):

            get_playlist = False
            search_term_parts = search_term.strip().split(' ')
            search_term = search_term_parts[0]

            youtube_id, playlist_id = cls._parse_url(search_term)

            if len(search_term_parts) == 2 and playlist_id is not None:
                if search_term_parts[1] in ['1', 'True', 'true']:
                    get_playlist = True

            if youtube_id is not None and not get_playlist:
                # return a Track object
                return cls.id_details(youtube_id)

            elif playlist_id is not None and get_playlist:
                # return a list of Track objects
                return cls.id_details(playlist_id, is_playlist_id=True)

            return None
        else:
            # search youtube by search term
            return cls._search(search_term, results)

    @classmethod
    def playlist_search(cls, search_term, results=5):
        """
        Search for a playlist matching the search term.

        :param search_term: The search term to search for.
        :type search_term: str
        :param results: The amount of playlist to return.
        :type results: int
        :return: A list containing `playlist_title` and `playlist_id`.
        :rtype: list | None
        """
        url = cls._playlist_search_url.format(API_KEY,
                                              web.quote(search_term.encode('UTF-8', 'ignore')))

        response = web.get(url=url, as_json=True, referer=REFERER)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            if 'items' in response.json:
                play_lists = []

                for i, item in enumerate(response.json['items']):

                    playlist_id = item['id']['playlistId']
                    playlist_title = item['snippet']['title']  #

                    play_list_info = {
                        'playlist_title': playlist_title,
                        'playlist_id': playlist_id
                    }
                    play_lists.append(play_list_info)

                    if i == results - 1:
                        break

                return play_lists

    @classmethod
    def id_details(cls, id_, is_playlist_id=False, is_youtube_id=False):
        """
        Get the details of a youtube ID.

        The ID can be both a video ID or a playlist ID.

        If it's a video ID a Track object is returned.
        If it's a playlist ID a list of Track object is returned.

        :param id_: The id to find details for.
        :type id_: str
        :param is_playlist_id: Is the ID a playlist ID.
        :type is_playlist_id: bool
        :param is_youtube_id: Is the ID a youtube ID.
        :type is_youtube_id: bool
        :return: A Track, a list of Tracks or None.
        :rtype: Track | list | None
        """
        if is_playlist_id:
            return cls._playlist_videos(id_)
        else:
            return cls._details(id_, check=False, is_youtube_id=is_youtube_id)

    # Private methods
    @classmethod
    def _playlist_videos(cls, playlist_id):
        url = cls._playlist_items_url.format(API_KEY, playlist_id)
        response = web.get(url=url, as_json=True, referer=REFERER)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            video_list = []
            if 'items' in response.json:

                for item in response.json['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                    track = cls._details(video_id)

                    if track is not None:
                        video_list.append(track)

            return video_list

    @classmethod
    def _is_youtube_url(cls, search_str):
        """
        Determine if the search string is a youtube url.

        :param search_str: The search term
        :type search_str: str
        :return: True if it is a youtube url
        :rtype: bool
        """
        for domain in ['youtube.com', 'youtu.be']:
            if domain in search_str:
                return True

        return False

    @classmethod
    def _is_youtube_id(cls, yid):
        if string_util.is_valid_string(yid, pattern='^[a-zA-Z0-9_-]{11}$'):
            return True
        return False

    @classmethod
    def _parse_url(cls, url):
        """
        Parse youtube ID and possible playlist ID from a youtube url.

        :param url: A youtube url.
        :type url: str
        :return: Youtube video ID and possible playlist ID.
        :rtype: tuple
        """
        video_id = None
        playlist_id = None

        parsed = web.parse_url(url)

        if parsed[2] == '/watch':  # could check for domain here
            # it is a youtube.com link
            if len(parsed[4]) == 13:
                # 13 is `v=` + a 11 characters long video ID
                # remove the `v=` part and return the video ID
                # (playlist_id will be None in this case)
                video_id = parsed[4].replace('v=', '')
            else:
                # if > 13 it is a playlist url
                # some playlist urls contain `start_radio=1`
                if 'start_radio' in parsed[4]:
                    # remove the `&start_radio=1` from the query string
                    query = parsed[4].replace('&start_radio=1', '')
                else:
                    query = parsed[4]
                # split the query string to parts
                parts = query.split('&')
                # some cleaning
                video_id = parts[0].replace('v=', '')
                playlist_id = parts[1].replace('list=', '')

        elif parsed[1] == 'youtu.be':
            # youtu.be links only contains a video ID, right..?
            video_id = parsed[2].replace('/', '')

        return video_id, playlist_id

    @classmethod
    def _search(cls, search_term, results=0):

        url = cls._search_url.format(API_KEY,
                                     web.quote(search_term.encode('UTF-8', 'ignore')))

        response = web.get(url=url, as_json=True, referer=REFERER)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            if 'items' in response.json:
                tracks = []
                for i, item in enumerate(response.json['items']):
                    video_id = item['id']['videoId']
                    details = cls._details(video_id)

                    if details is not None:
                        tracks.append(details)

                        if results == 0 and len(tracks) == 1:
                            break

                        elif results > 0 and results == len(tracks):
                            break

                if results == 0 and len(tracks) > 0:
                    return tracks[0]

                if len(tracks) > 0:
                    return tracks
                else:
                    return None

            return None

    @classmethod
    def _is_blocked(cls, blocked):
        log.debug('blocked in: %s, ALLOWED_COUNTRIES: %s' % (blocked, ALLOWED_COUNTRIES))
        if len(ALLOWED_COUNTRIES) > 0:

            for country in ALLOWED_COUNTRIES:
                if country in blocked:
                    return True
            return False

        return False

    @classmethod
    def _is_allowed(cls, allowed):
        log.debug('allowed in: %s, ALLOWED_COUNTRIES: %s' % (allowed, ALLOWED_COUNTRIES))
        if len(ALLOWED_COUNTRIES) > 0:

            for country in ALLOWED_COUNTRIES:
                if country not in allowed:
                    return False
            return True

        return True

    @classmethod
    def _details(cls, video_id, check=True, is_youtube_id=False):

        log.debug('video details for: %s, check: %s' % (video_id, check))

        url = cls._video_details_url.format(API_KEY, video_id)
        response = web.get(url=url, as_json=True, referer=REFERER)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            if 'items' in response.json:

                is_embeddable = True
                track = None

                if len(response.json['items']) != 0:

                    item = response.json['items'][0]

                    # does deleted videos contain contentDetails?
                    if 'contentDetails' in item:

                        if 'status' in item:
                            if 'embeddable' in item['status']:
                                is_embeddable = item['status']['embeddable']

                                if not is_youtube_id and not is_embeddable:
                                    return track  # None

                                if not is_embeddable:
                                    is_embeddable = False

                        content_details = item['contentDetails']

                        if check:

                            if 'regionRestriction' in content_details:
                                if 'blocked' in content_details['regionRestriction']:
                                    blocked = content_details['regionRestriction']['blocked']
                                    if cls._is_blocked(blocked):
                                        return track

                                if 'allowed' in content_details['regionRestriction']:
                                    allowed = content_details['regionRestriction']['allowed']
                                    if not cls._is_allowed(allowed):
                                        return track

                        video_time = string_util.convert_to_seconds(content_details['duration'])
                        video_title = response.json['items'][0]['snippet']['title']
                        image_medium = response.json['items'][0]['snippet']['thumbnails']['medium']['url']

                        track = Track(video_id=video_id, video_time=video_time,
                                      video_title=video_title, image=image_medium, embeddable=is_embeddable)

                return track
