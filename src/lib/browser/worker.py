# -*- coding: utf-8 -*-

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Development Team: Stanislav WEB
"""

import threading
import time
from Queue import Empty as QueueEmptyError
from threading import BoundedSemaphore, Event

from src.core import process
from src.lib.tpl import Tpl as tpl


class Worker(threading.Thread):
    """Worker class"""

    def __init__(self, queue, num_threads, timeout=None):
        """
        Init thread worker
        :param Queue.Queue queue: simple queue object
        :param int num_threads: threads numbers
        :param int timeout: delay timeout
        """

        super(Worker, self).__init__()
        self.__semaphore = BoundedSemaphore(num_threads)
        self.__event = Event()
        self.__event.set()
        self.__empty = False
        self.__running = True
        self.__exception = None
        self.__queue = queue
        self.__timeout = timeout
        self.counter = 0

    def pause(self):
        """
        Pause current worker
        :return: None
        """

        self.__running = False
        self.__event.clear()

    def resume(self):
        """
        Resume current worker
        :return: None
        """

        self.__running = True
        self.__event.set()

    @property
    def exception(self):
        """
        Return exception message
        :return:
        """

        return self.__exception

    def run(self):
        """
        Run current worker
        :return: None
        """

        try:

            self.__event.wait()

            while self.__running:

                if 0 < self.__timeout:
                    time.sleep(self.__timeout)

                try:

                    func, args, kargs = self.__queue.get(block=True)
                    self.counter += 1
                    func(*args, **kargs)
                    self.__queue.task_done()

                except QueueEmptyError:
                    self.__empty = True

                finally:
                    if not self.__event.isSet():
                        self.__semaphore.release()
                        self.__event.wait()
        except Exception as e:
            self.terminate(e)

    @classmethod
    def terminate(cls, msg):
        """
        Terminate thread
        :param str msg: output message
        :return: None
        """

        tpl.error(msg)
        process.kill()
