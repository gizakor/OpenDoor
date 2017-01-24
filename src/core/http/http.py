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

from urllib3 import HTTPConnectionPool
from urllib3.exceptions import MaxRetryError, ReadTimeoutError, HostChangedError

from src.core import helper
from .exceptions import HttpRequestError
from .providers import RequestProvider


class HttpRequest(RequestProvider):
    """HttpRequest class"""

    def __init__(self, config, debug=0, **kwargs):
        """
        Request instance
        :param src.lib.browser.config.Config config:
        :param int debug: debug flag
        """

        try:

            self.__tpl = kwargs.get('tpl')
            RequestProvider.__init__(self, config, agent_list=kwargs.get('agent_list'))

        except (TypeError, ValueError) as e:
            raise HttpRequestError(e.message)

        self.__assert_same_host = True if 'directories' == config.scan else False
        self.__cfg = config
        self.__debug = False if debug < 2 else True
        self.__pool = self.__http_pool()

    def __http_pool(self):
        """
        Create HTTP connection pool
        :raise HttpRequestError
        :return: urllib3.HTTPConnectionPool
        """

        try:
            if True is self.__debug:
                self.__tpl.debug(key='http_pool_start')

            pool = HTTPConnectionPool(self.__cfg.host, port=self.__cfg.port, maxsize=self.__cfg.threads,
                                      timeout=self.__cfg.timeout, block=True)
            return pool
        except Exception as e:
            raise HttpRequestError(e)

    def request(self, url):
        """
        Client request HTTP
        :param str url: request uri
        :return: urllib3.HTTPResponse
        """

        # import httplib
        # httplib.HTTPConnection.debuglevel = 5

        try:
            response = self.__pool.request(self.__cfg.method, helper.parse_url(url).path,
                                           headers=self._headers,
                                           retries=self.__cfg.retries,
                                           assert_same_host=self.__assert_same_host,
                                           redirect=False)

            self.cookies_middleware(is_accept=self.__cfg.accept_cookies, response=response)
            return response

        except MaxRetryError:
            self.__tpl.warning(key='max_retry_error', url=helper.parse_url(url).path)
            pass
        except HostChangedError as e:
            self.__tpl.warning(key='host_changed_error', details=e)
            pass
        except ReadTimeoutError:
            self.__tpl.warning(key='read_timeout_error', url=helper.parse_url(url).path)
            pass