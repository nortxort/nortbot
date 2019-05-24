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

# Slightly modified from:
# https://stackoverflow.com/questions/3033952/threading-pool-similar-to-the-multiprocessing-pool
# and/or http://code.activestate.com/recipes/577187-python-thread-pool/

import threading
import Queue

import logging


log = logging.getLogger(__name__)


class Timer:
    """
    Timer class for time based calls.
    """

    def __init__(self):
        self._timer_thread = None

    @property
    def is_alive(self):
        """
        Check if the timer is running.

        :return: True if running, else False.
        :rtype: bool
        """
        if self._timer_thread is not None:
            if self._timer_thread.is_alive():
                return True
            return False
        return False

    def start(self, func, event_time):
        """
        Start an time based event.

        :param func: The function/method to call
        once the time have been reached.
        :param event_time: The time before the
        function/method will be called
        :type event_time: int | float | long
        """
        log.debug('starting timer. func: `%s`' % func)
        self._timer_thread = threading.Timer(event_time, func)
        self._timer_thread.start()

    def cancel(self):
        """
        Cancel the timer.

        :return: True if canceled, else False.
        :rtype: bool
        """
        log.debug('canceling timer.')
        if self._timer_thread is not None:
            if self.is_alive:
                self._timer_thread.cancel()
                self._timer_thread = None
                return True
            return False
        return False


class Worker(threading.Thread):
    """
    A worker class.
    """

    def __init__(self, tasks):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        """
        Overrides Thread.run
        """
        while True:
            func, args, kwargs = self.tasks.get()
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(e)
            finally:
                self.tasks.task_done()


class ThreadPool:
    """
    A thread pool class.

    This allows us to have a pool of threads
    to use from. Once a thread is done, it will be
    added back in to the pool.
    """

    def __init__(self, num_threads):
        """
        Initialize the thread pool class.

        :param num_threads: The amount of threads in the pool.
        :type num_threads: int
        """
        log.info('initiating thread pool (%s)' % num_threads)
        self.tasks = Queue.Queue(num_threads)

        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kwargs):
        """
        Add a task to the thread pool.

        :param func: The function/method to call in a thread.
        :param args: Function/method arguments.
        :param kwargs: Function/method keywords.
        """
        log.debug('adding task, func=%s, args=%s, kwargs=%s' %
                  (func, args, kwargs))
        self.tasks.put((func, args, kwargs))

    def map(self, func, args_list):
        """

        :param func:
        :type func:
        :param args_list:
        :type args_list:
        """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """
        Wait for all threads in the pool to be done.
        """
        self.tasks.join()


def thread_task(target, *args):
    """
    Create a simple threaded task.

    NOTE: This wraps up treading.Thread(..).start()

    :param target: The function/method to call in a thread.
    :param args: Function/method arguments.
    """
    log.debug('threaded task, target=%s, args=%s' % (target, args))
    t = threading.Thread(target=target, args=args)
    # t.daemon = True
    t.start()
    return t
