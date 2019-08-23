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

# code modified from https://github.com/lu-ci/apex-sigma-core/tree/master/sigma/modules/searches/wikipedia


import logging
from util import web

log = logging.getLogger(__name__)


class WikiResponse:
    """
    Represents a wikipedia response.
    """
    def __init__(self, wiki_data):
        self._data = wiki_data

    @property
    def has_data(self):
        """
        If there is data from the wikipedia request.

        :return: True if there is wikipedia data.
        :rtype: bool
        """
        if self._data is not None and \
                len(self._data) == 4 and len(self._data[1]) >= 1:
            return True

        return False

    @property
    def title(self):
        """
        The title of the wikipedia request.

        :return: Wikipedia title.
        :rtype: str
        """
        if self.has_data:
            return self._data[1][0]

        return None

    @property
    def summary(self):
        """
        The summary of the wikipedia request.

        :return: wikipedia summary.
        :rtype: str
        """
        if self.has_data:
            return self._data[2][0]

        return None

    @property
    def link(self):
        """
        The link to the wikipedia request source.

        :return: In depth wikipedia reading link.
        :rtype: str
        """
        if self.has_data:
            return self._data[3][0]

        return None


class WikiPedia(object):
    """
    A wikipedia class to do wikipedia searches with.
    """
    base_url = 'https://en.wikipedia.org/w/api.php?format=json{0}'

    @classmethod
    def search(cls, search_term):
        """
        Search wikipedia APi for a search term.

        :param search_term: The search term to search for.
        :type search_term: str
        :return: A WikiResponse.
        :rtype: WikiResponse
        """
        search = web.quote(search_term.encode('UTF-8', 'ignore'))
        url = cls.base_url.format('&action=opensearch&search=%s&redirects=resolve' % search)
        response = web.get(url=url, as_json=True)

        if len(response.errors) > 0:
            log.debug(response.errors)
        else:
            # response.json is always 4, even if there is no such thing

            # response.json[0] is the search term
            # response.json[1] is a list a possible response titles
            # response.json[2] is a list of summaries
            # response.json[3] is a list of links to the actual wikipedia pages

            return WikiResponse(response.json)
