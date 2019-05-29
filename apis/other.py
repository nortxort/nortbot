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

import re
import logging
import xml.etree.ElementTree
from util import web

log = logging.getLogger(__name__)

# API key for the weather
WEATHER_API_KEY = None


def urbandictionary_search(search):
    """
    Searches urbandictionary's API for a given search term.

    :param search: The search term to search for.
    :type search: str
    :return: urbandictionary definition or None on no match or error.
    :rtype: str | None
    """
    if str(search).strip():
        urban_api_url = 'http://api.urbandictionary.com/v0/define?term=%s' % search
        response = web.get(url=urban_api_url, as_json=True)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            try:
                _definition = response.json['list'][0]['definition']
                definition = re.sub(r"\[*\]*", "", _definition) 
                return definition.encode('ascii', 'ignore')
            except (KeyError, IndexError):
                return None
    else:
        return None


def weather_search(city):
    """
    Searches apixu.com's API for weather data for a given city.
    You must have a working API key to be able to use this function.

    :param city: The city name to search for.
    :type city: str
    :return: weather data or None on no match or error.
    :rtype: str | None
    """
    if str(city).strip():
        if WEATHER_API_KEY is None:
            return 'Missing api key.'
        else:
            weather_api_url = 'https://api.apixu.com/v1/current.json?key=%s&q=%s' % \
                              (WEATHER_API_KEY, city)

            response = web.get(url=weather_api_url, as_json=True)
            if len(response.errors) > 0:
                log.error(response.errors)
                return None

            elif 'error' in response.json:
                return response.json['error']['message']

            else:
                try:
                    pressure = response.json['current']['pressure_mb']
                    temp_c = response.json['current']['temp_c']
                    temp_f = response.json['current']['temp_f']
                    query = response.json['location']['name']
                    country = response.json['location']['country']
                    result = '%s(%s) Temperature: %sC (%sF) Pressure: %s millibars' % \
                             (query, country, temp_c, temp_f, pressure)
                    return result
                except (IndexError, KeyError) as e:
                    log.error(e)
    else:
        return None


def whois(ip):
    """
    Searches ip-api for information about a given IP.

    :param ip: The ip or domain to search for.
    :type ip: str
    :return: Who is information or None on error.
    :rtype: str | None
    """
    if str(ip).strip():
        url = 'http://ip-api.com/json/%s' % ip
        response = web.get(url=url, as_json=True)

        if len(response.errors) > 0:
            log.error(response.errors)
            return None
        else:
            try:
                city = response.json['city']
                country = response.json['country']
                isp = response.json['isp']
                org = response.json['org']
                region = response.json['regionName']
                zipcode = response.json['zip']
                info = "%s, %s, %s, %s, %s" % \
                (country, city, region, zipcode, isp)
                return info
            except KeyError as ke:
                log.error(ke)
                return None
    else:
        return None


def chuck_norris():
    """
    Finds a random Chuck Norris joke/quote.

    :return: joke or None on failure.
    :rtype: str | None
    """
    url = 'http://api.icndb.com/jokes/random/?escape=javascript'
    response = web.get(url=url, as_json=True)

    if len(response.errors) > 0:
        log.error(response.errors)
        return None
    else:
        if response.json['type'] == 'success':
            joke = response.json['value']['joke']
            return joke

        return None


def instagram_search(search_name, results=5):
    """
    Search instagram for a name matching the search name.

    :param search_name: The name of the instagram user to search for.
    :type search_name: str
    :param results: The amount of results.
    :type results: int
    :return: A list of instagram user matching the search.
    :rtype: list
    """
    url = 'https://www.instagram.com/web/search/topsearch/?context=blended&query=%s' % search_name
    response = web.get(url=url, as_json=True)

    users = []
    if len(response.errors) > 0:
        log.error(response.errors)
        return users
    else:
        if response.json['status'] == 'ok':
            for i, user in enumerate(response.json['users']):

                user_data = {
                    'username': user['user']['username'],
                    'byline': user['user']['byline'],
                    'follower_count': user['user']['follower_count'],
                    'is_private': user['user']['is_private'],
                    'url': 'https://www.instagram.com/%s' % user['user']['username']
                }

                users.append(user_data)
                if i == results - 1:
                    break

        return users


def porn(keyword):
    """
    Searches the API of eporner.com for videos matching the keyword.

    :param keyword: The porn keyword to search for.
    :type keyword: str
    :return: A list of matching videos.
    :rtype: list
    """
    movies = []
    if len(keyword) >= 3:
        # TODO: Maybe replace anything not [a-zA-Z0-9] in keyword with -
        url = 'https://www.eporner.com/api_xml/%s/5' % keyword
        response = web.get(url=url)

        if len(response.errors) > 0:
            log.error(response.errors)
            return movies
        else:

            xml_doc = xml.etree.ElementTree.fromstring(response.content)

            for movie in xml_doc:
                url = 'https://www.eporner.com/embed/%s' % movie.find('sid').text
                movies.append(url)

    return movies
