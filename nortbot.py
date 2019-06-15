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

import bot
from util import thread_task


log = logging.getLogger(__name__)


def logger_setup():
    if bot.CONF.DEBUG_TO_FILE:

        fmt = '%(asctime)s : %(levelname)s : %(filename)s : ' \
              '%(lineno)d : %(funcName)s() : %(name)s : %(message)s'

        logging.basicConfig(filename=bot.CONF.DEBUG_FILE_NAME,
                            level=bot.CONF.DEBUG_LEVEL, format=fmt)
    else:
        log.addHandler(logging.NullHandler)


def main():
    if bot.CONF.ROOM is None:
        bot.CONF.ROOM = raw_input('Enter room name: ').strip()

    if bot.CONF.NICK is None:
        bot.CONF.NICK = raw_input('Enter nickname (optional): ').strip()

    if bot.CONF.ACCOUNT is not None and bot.CONF.PASSWORD is not None:
        bot_client = bot.NortBot(bot.CONF.ROOM, nick=bot.CONF.NICK,
                                 account=bot.CONF.ACCOUNT,
                                 password=bot.CONF.PASSWORD)
    else:
        bot_client = bot.NortBot(bot.CONF.ROOM, nick=bot.CONF.NICK)

    if bot.CONF.AUTO_LOGIN:
        do_login = True
    else:
        do_login = raw_input('Login? [enter=no] ')

    if do_login:
        if bot_client.account is None:
            bot_client.account = raw_input('Account: ').strip()
        if bot_client.password is None:
            bot_client.password = raw_input('Password: ')

        is_logged_in = bot_client.login()
        while not is_logged_in:
            bot_client.account = raw_input('Account: ').strip()
            if bot_client.account == '/':
                main()
                break
            bot_client.password = raw_input('Password: ')
            if bot_client.password == '/':
                main()
                break
            else:
                if bot_client.password == '//' or bot_client.password == '//':
                    do_login = False
                    break
                else:
                    is_logged_in = bot_client.login()

        if not do_login:
            bot_client.account = None
            bot_client.password = None

    thread_task(bot_client.connect)

    while not bot_client.connected:
        time.sleep(2)


if __name__ == '__main__':

    logger_setup()

    log.info('Starting Nortbot v %s' % bot.CONF.BOT_VERSION)

    main()
