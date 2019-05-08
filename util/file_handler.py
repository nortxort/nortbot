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
import codecs
import os
import logging

log = logging.getLogger(__name__)


def reader(file_path, file_name):
    """
    Reads from a file.

    :param file_path: The path to the file.
    :type file_path: str
    :param file_name: The name of the file.
    :type file_name: str
    :return: A list of lines or empty list on error.
    :rtype: list
    """
    file_content = []
    if os.path.exists(file_path):
        if os.path.isfile(file_path + file_name):
            try:
                with codecs.open(file_path + file_name, encoding="utf-8") as f:
                    for line in f:
                        file_content.append(line.rstrip('\n'))
            except IOError as ioe:
                log.error('failed to read file: %s path: %s IOError: %s' %
                          (file_name, file_path, ioe))
            finally:
                return file_content
    return file_content


def writer(file_path, file_name, write_this):
    """
    Write to file line by line.

    :param file_path: The path to the file.
    :type file_path: str
    :param file_name: The name of the file.
    :type file_name: str
    :param write_this: The content to write to file.
    :type write_this: str
    """
    # maybe return True if we could write and False if not
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with codecs.open(file_path + file_name, mode='a', encoding="utf-8") as f:
        f.write(write_this + '\n')


def delete_file(file_path, file_name):
    """
    Deletes a file entirely.

    :param file_path: The path to the file.
    :type file_path: str
    :param file_name: The name of the file.
    :type file_name: str
    :return: True if deleted, else False
    :rtype: bool
    """
    if os.path.isfile(file_path + file_name):
        os.remove(file_path + file_name)
        return True
    return False


def delete_file_content(file_path, file_name):
    """
    Deletes all content from a file.

    :param file_path: The path to the file.
    :type file_path: str
    :param file_name: The name of the file.
    :type file_name: str
    """
    open(file_path + file_name, mode='w').close()


def remove_from_file(file_path, file_name, remove):
    """
    Removes a line from a file.

    :param file_path: The path to the file.
    :type file_path: str
    :param file_name: The name of the file.
    :type file_name: str
    :param remove: The line to remove.
    :type remove: str
    :return: True on success else False
    :rtype: bool
    """
    file_list = reader(file_path, file_name)
    if len(file_list) > 0:
        if remove in file_list:
            file_list.remove(remove)
            delete_file_content(file_path, file_name)
            for line in file_list:
                writer(file_path, file_name, line)
            return True
        return False
    return False
