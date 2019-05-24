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
from youtube import Youtube, Track

# TODO: Create LastFM class

CHART_URL = 'http://lastfm-ajax-vip1.phx1.cbsig.net/kerve/charts?nr={0}&type=track&format=json'

TAG_SEARCH_URL = 'http://lastfm-ajax-vip1.phx1.cbsig.net/kerve/charts?nr={0}&type=track&f=tag:{1}&format=json'

LISTENING_NOW_URL = 'http://lastfm-ajax-vip1.phx1.cbsig.net/kerve/listeningnow?limit={0}&format=json'


log = logging.getLogger(__name__)


def chart(chart_items=5):
    """
    Finds the currently most played tunes on last.fm and
    returns them as a list of Track objects.

    :param chart_items: The amount of tracks wanted.
    :type chart_items: int
    :return: A list of Track objects or None on error.
    :rtype: list | None
    """
    url = CHART_URL.format(chart_items)
    lastfm = web.get(url=url, as_json=True)

    log.debug('lastfm response %s' % lastfm.json)

    if len(lastfm.errors) > 0:
        log.error(lastfm.errors)
        return None
    else:
        if 'results' in lastfm.json:
            if 'track' in lastfm.json['results']:
                if len(lastfm.json['results']['track']) != 0:

                    yt_tracks = []
                    for track in lastfm.json['results']['track']:
                        search_str = '%s-%s' % (track['artist'], track['name'])
                        yt = Youtube.search(search_str)

                        log.debug(yt)

                        if isinstance(yt, Track):
                            yt_tracks.append(yt)

                    return yt_tracks

                return None


def tag_search(search_str, by_id=True, max_tunes=40):
    """
    Search last.fm for tunes matching the search term
    and turns them in to a youtube list of Tracks objects.

    :param search_str: Search term to search for.
    :type search_str: str
    :param by_id: If True, only tunes that have a youtube id will be added(recommended)
    :type by_id: bool
    :param max_tunes: The max amount of tunes to return.
    :type max_tunes: int
    :return: A list of Track objects.
    :rtype list | None
    """
    url = TAG_SEARCH_URL.format(max_tunes, web.quote(search_str))
    lastfm = web.get(url=url, as_json=True)

    log.debug('lastfm response %s' % lastfm.json)

    if len(lastfm.errors) > 0:
        log.error(lastfm.errors)
        return None
    else:
        if 'track' in lastfm.json['results']:
            if len(lastfm.json['results']['track']) is not 0:
                yt_tracks = []

                for track in lastfm.json['results']['track']:
                    search_str = '%s-%s' % (track['artist'], track['name'])
                    if 'playlink' in track:

                        if 'data-youtube-id' in track['playlink']:
                            youtube_id = track['playlink']['data-youtube-id']
                            yt = Youtube.id_details(youtube_id)
                            log.debug(yt)
                            if yt is not None:
                                yt_tracks.append(yt)

                        else:
                            if not by_id:
                                yt = Youtube.search(search_str)
                                log.debug(
                                    'search by search string: %s result: %s' % (search_str, yt))
                                if yt is not None:
                                    yt_tracks.append(yt)

                    else:
                        if not by_id:
                            yt = Youtube.search(search_str)
                            log.debug(
                                'search by search string: %s result: %s' % (search_str, yt))
                            if yt is not None:
                                yt_tracks.append(yt)

                return yt_tracks


def listening_now(max_tunes, by_id=True):
    """
    Get a list of tunes other people using last.fm are listening to,
    and turn them in to a youtube list of Tracks objects.

    TODO: this might need a little more work

    :param max_tunes: The amount of Tracks.
    :type max_tunes: int
    :param by_id: Only add tunes that have a youtube ID(recommended)
    :type by_id: bool
    :return: A list of Track objects
    :rtype: list | None
    """
    url = LISTENING_NOW_URL.format(max_tunes)
    lastfm = web.get(url=url, as_json=True)

    log.debug('lastfm response %s' % lastfm.json)

    if len(lastfm.json['Users']) != 0:
        yt_tracks = []
        for user in lastfm.json['Users']:
            if 'playlink' in user:
                if 'data-youtube-id' in user['playlink']:
                    youtube_id = user['playlink']['data-youtube-id']
                    yt = Youtube.id_details(youtube_id)
                    log.debug(yt)

                    if isinstance(yt, Track):
                        yt_tracks.append(yt)
            else:
                if 'Track' in user:
                    search_str = '%s-%s' % (user['Track']['Artist'], user['Track']['Name'])
                    if not by_id:
                        yt = Youtube.search(search_str)
                        log.debug('search by search string: %s result: %s' %
                                  (search_str, yt))
                        if isinstance(yt, Track):
                            yt_tracks.append(yt)

            return yt_tracks

        return None
