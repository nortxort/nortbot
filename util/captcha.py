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

import time
import logging
import web

__all__ = ['CAPTCHA_TIMEOUT', 'MAX_TRIES',
           'AntiCaptcha', 'AntiCaptchaError',
           'InvalidApiKey', 'NoFundsError',
           'MaxTriesError', 'AntiCaptchaApiError']

log = logging.getLogger(__name__)

CAPTCHA_TIMEOUT = 10  # type: int
MAX_TRIES = 5         # type: int


class AntiCaptchaError(Exception):
    """
    Anti captcha base exception.
    """
    pass


class InvalidApiKey(AntiCaptchaError):
    """
    Raised on invalid API key.
    """
    pass


class NoFundsError(AntiCaptchaError):
    """
    Raised when no funds available.
    """
    pass


class MaxTriesError(AntiCaptchaError):
    """
    Raised  when max tries has been reached.
    """
    pass


class AntiCaptchaApiError(AntiCaptchaError):
    """
    Anti captcha APi error.
    """

    def __init__(self, **error):
        self.id = error.get('errorId')
        self.code = error.get('errorCode')
        self.description = error.get('errorDescription')


class CaptchaResponse:
    """
    Class representing a captcha response.
    """

    def __init__(self, tries, **data):
        self._tries = tries
        self._data = data

    @property
    def tries(self):
        """
        The amount of tries to fetch the response.

        :return: Tries to fetch the response.
        :rtype: int
        """
        return self._tries

    @property
    def solution(self):
        """
        The solution object.

        :return: Solution object.
        :rtype: dict
        """
        return self._data.get('solution')

    @property
    def token(self):
        """
        The gRecaptchaResponse token.

        :return: gRecaptchaResponse token
        :rtype: str | None
        """
        if self.solution is not None:
            return self.solution.get('gRecaptchaResponse')
        return None

    @property
    def cost(self):
        """
        Te cost of the captcha task.

        :return: The cost of the task.
        """
        return self._data.get('cost')

    @property
    def solve_time(self):
        """
        The amount of time it took to solve the task.

        :return: Time it took for the task.
        :rtype: int
        """
        start_time = self._data.get('createTime', 0)
        end_time = self._data.get('endTime', 0)
        return end_time - start_time

    @property
    def workers(self):
        """
        Number of workers who tried to complete the task.

        :return: Number of workers.
        :rtype: int
        """
        return self._data.get('solveCount')


class AntiCaptcha:
    """
    Anti captcha class for https://api.anti-captcha.com
    """

    def __init__(self, page_url, api_key):
        """
        Initialize the anti captcha class.

        :param page_url: The url of the captcha.
        :type page_url: str
        :param api_key: A anti-captcha API key.
        :type api_key: str
        """
        self._page_url = page_url
        self._api_key = api_key

        self._site_key = ''
        self._task_id = 0

        if len(self._api_key) != 32:
            raise InvalidApiKey('the api key `%s` is invalid. len=%s' %
                                (self._api_key, len(self._api_key)))

    def balance(self):
        """
        Get the balance for an API key.

        :return: The balance of an API key
        :rtype: int | float
        """
        post_data = {
            'clientKey': self._api_key
        }
        url = 'https://api.anti-captcha.com/getBalance'
        pr = web.post(url=url, json=post_data, as_json=True)

        if len(pr.errors) > 0:
            log.error(pr.errors)
        else:
            if pr.json['errorId'] > 0:
                raise AntiCaptchaApiError(**pr.json)
            else:
                return pr.json['balance']

    def solver(self, site_key):
        """
        Initiate the captcha solving service.

        :param site_key: The site key.
        :type site_key: str
        :return: A CaptchaResponse object.
        :rtype: CaptchaResponse
        """
        self._site_key = site_key
        return self._create_task()

    def _create_task(self):
        """
        Create a captcha solving task.
        """
        log.info('creating anti-captcha task.')

        post_data = {
            'clientKey': self._api_key,
            'task':
                {
                    'type': 'NoCaptchaTaskProxyless',
                    'websiteURL': self._page_url,
                    'websiteKey': self._site_key
                }
        }

        url = 'https://api.anti-captcha.com/createTask'

        pr = web.post(url=url, json=post_data, as_json=True)

        if len(pr.errors) > 0:
            log.error(pr.errors)
        else:
            if pr.json['errorId'] > 0:
                if pr.json['errorId'] == 10:
                    raise NoFundsError('no funds for `%s`' % self._api_key)
                else:
                    raise AntiCaptchaApiError(**pr.json)
            else:
                self._task_id = pr.json['taskId']
                log.debug('anti-captcha task id: %s' % self._task_id)
                return self._task_waiter()

    def _task_result(self):
        """
        Get the task result.
        """
        post_data = {
            'clientKey': self._api_key,
            'taskId': self._task_id
        }

        url = 'https://api.anti-captcha.com/getTaskResult'

        pr = web.post(url=url, json=post_data, as_json=True)

        if len(pr.errors) > 0:
            log.error(pr.errors)
        else:
            if pr.json['errorId'] > 0:
                raise AntiCaptchaApiError(**pr.json)
            else:
                log.debug('task result: %s' % pr.json)
                return pr.json

    def _task_waiter(self):
        """
        Wait for the task result to be done.

        :return: A CaptchaResponse object.
        :rtype: CaptchaResponse
        """
        if self._task_id == 0:
            log.debug('no task id `%s`' % self._task_id)
            return None
        else:
            log.info('starting anti-captcha task waiter.')

            tries = 1
            while True:
                log.debug('waiting %s for result. try=%s' %
                          (CAPTCHA_TIMEOUT, tries))
                time.sleep(CAPTCHA_TIMEOUT)

                solution = self._task_result()
                if solution['status'] == 'ready':
                    return CaptchaResponse(tries, **solution)

                if tries == MAX_TRIES:
                    raise MaxTriesError('max tries %s reached.' % MAX_TRIES)

                tries += 1
