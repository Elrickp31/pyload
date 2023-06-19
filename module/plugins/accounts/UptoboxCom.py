# -*- coding: utf-8 -*-

import re
import time

from ..internal.XFSAccount import XFSAccount
from ..internal.misc import search_pattern


class UptoboxCom(XFSAccount):
    __name__ = "UptoboxCom"
    __type__ = "account"
    __version__ = "0.27"
    __status__ = "testing"

    __description__ = """Uptobox.com account plugin"""
    __license__ = "GPLv3"
    __authors__ = [("Elrick", "elrick69[AT]rocketmail[DOT]com"),
                   ("benbox69", "dev@tollet.me"),
                   ("GammaC0de", "nitzo2001[AT]yahoo[DOT]com")]

    PLUGIN_DOMAIN = "uptobox.eu"
    PLUGIN_URL = "https://uptobox.eu/"
    
    LOGIN_URL = "https://uptobox.eu/login"
    LOGIN_SKIP_PATTERN = r"https://uptobox\.eu/logout"

    PREMIUM_PATTERN = r'Premium member'
    VALID_UNTIL_PATTERN = r"class='expiration-date .+?'>(\d{1,2} [\w^_]+ \d{4})"

    def grab_info(self, user, password, data):
        validuntil = None
        trafficleft = None
        leechtraffic = None
        premium = None

        self.data = self.load(self.PLUGIN_URL, #+"my_account")
                              get={'op': "my_account"},
                              cookies=self.COOKIES)
        premium = True if search_pattern(self.PREMIUM_PATTERN, self.data) else False

        m = search_pattern(self.VALID_UNTIL_PATTERN, self.data)
        if m is not None:
            expiredate = m.group(1).strip()
            self.log_debug("Expire date: " + expiredate)

            try:
                validuntil = time.mktime(time.strptime(expiredate, "%Y-%m-%d"))

            except Exception, e:
                self.log_error(e)

            else:
                self.log_debug("Valid until: %s" % validuntil)

                if validuntil > time.mktime(time.gmtime()):
                    premium = True
                    trafficleft = -1
                else:
                    premium = False
                    validuntil = None  #: Registered account type (not premium)
        else:
            self.log_debug("VALID UNTIL PATTERN not found")

        return {'validuntil': validuntil,
                'trafficleft': trafficleft,
                'leechtraffic': leechtraffic,
                'premium': premium}


    def signin(self, user, password, data):
        html = self.load(self.LOGIN_URL, cookies=self.COOKIES)

        if re.search(self.LOGIN_SKIP_PATTERN, html):
            self.skip_login()

        html = self.load(self.LOGIN_URL,
                         post={'login': user,
                               'password': password},
                         ref=self.LOGIN_URL,
                         cookies=self.COOKIES)

        if re.search(self.LOGIN_SKIP_PATTERN, html) is None:
            self.fail_login()
