#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of IVRE.
# Copyright 2011 - 2015 Pierre LALET <pierre.lalet@cea.fr>
#
# IVRE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IVRE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IVRE. If not, see <http://www.gnu.org/licenses/>.

"""This sub-module handles configuration values.

It contains the (hard-coded) default values, which can be overwritten
by ~/.ivre.conf, /usr/local/etc/ivre/ivre.conf,
/usr/local/etc/ivre.conf, /etc/ivre/ivre.conf and/or
/etc/ivre.conf.

"""

import os
import stat

# Default values:
DB = "mongodb:///ivre"
BULK_UPSERTS_MAXSIZE = 100
DEBUG = False
# specific: if no value is specified for *_PATH variables, they are
# going to be constructed by guessing the installation PREFIX (see the
# end of this file).
GEOIP_PATH = None
HONEYD_IVRE_SCRIPTS_PATH = None
AGENT_MASTER_PATH = "/var/lib/ivre/master"
TESSERACT_CMD = "tesseract"

NMAP_CMD = "nmap"
NMAP_SCAN_TYPE = ['sS', 'A']
NMAP_PING_TYPE = ['PS', 'PE']
NMAP_VERBOSITY = 2
NMAP_RESOLVE_LEVEL = 1
NMAP_PORTSPEC = "normal"
NMAP_OPT_PORTS = {
    'fast': ['-F'],
    'normal': [],
    'more': ['--top-ports', '2000'],
    'all': ['-p', '-'],
}
NMAP_HOST_TIMEOUT = "15m"
NMAP_SCRIPT_CATEGORIES = ['default', 'discovery', 'auth']
NMAP_SCRIPT_EXCLUDE = [
    # Categories we don't want
    'broadcast', 'brute', 'dos', 'exploit', 'external', 'fuzzer',
    'intrusive',
]
NMAP_SCRIPT_FORCE = []
NMAP_EXTRA_OPTIONS = None

WEB_ALLOWED_REFERERS = None
WEB_MAXRESULTS = None
WEB_WARN_DOTS_COUNT= 20000
WEB_GET_NOTEPAD_PAGES = None
# if overwritten, these two values must match those in the config.js
# config file config.dflt.skip and config.dflt.limit.
WEB_SKIP = 0
WEB_LIMIT = 10
# access control disabled by default:
WEB_INIT_QUERIES = {}
WEB_DEFAULT_INIT_QUERY = None

## Basic ACL example (to be put in /etc/ivre.conf):
# from ivre.db import db
# INIT_QUERIES = {
#     'admin': db.nmap.flt_empty,
#     'admin-site-a': db.nmap.searchcategory('site-a'),
#     'admin-scanner-a': db.nmap.searchsource('scanner-a')
# }
# DEFAULT_INIT_QUERY = db.nmap.searchhost('inexistant')

## More complex ACL example with realm handling (to be put in
## /etc/ivre.conf)
# class Users(object):
#     def __init__(self, Users={}, Realms={}):
#         self.Users = Users
#         self.Realms = Realms
#     def get(self, user, default):
#         if type(user) is str and '@' in user:
#             realm = user[user.index('@')+1:]
#         else: realm = None
#         return self.Users.get(user, self.Realms.get(realm, default))
# from ivre.db import db
# INIT_QUERIES = Users(Users={"admin": db.nmap.flt_empty},
#                      Realms={"admin.sitea": db.nmap.searchcategory('sitea')})
# DEFAULT_INIT_QUERY = db.nmap.searchhost('inexistant')


def get_config_file(paths=None):
    """Generates (yields) the available config files, in the correct order."""
    if paths is None:
        paths = [os.path.join(path, 'ivre.conf')
                 for path in ['/etc', '/etc/ivre', '/usr/local/etc',
                              '/usr/local/etc/ivre']]
        paths.append(os.path.join(os.path.expanduser('~'), '.ivre.conf'))
    for path in paths:
        if os.path.isfile(path):
            yield path

for fname in get_config_file():
    execfile(fname)

def guess_prefix(directory=None):
    """Attempts to find the base directory where IVRE components are
    installed.

    """
    def check_candidate(path, directory=None):
        """Auxilliary function that checks whether a particular
        path is a good candidate.

        """
        candidate = os.path.join(path, 'share', 'ivre')
        if directory is not None:
            candidate = os.path.join(candidate, directory)
        try:
            if stat.S_ISDIR(os.stat(candidate).st_mode):
                return candidate
        except OSError:
            pass
    if __file__.startswith('/'):
        path = '/'
        # absolute path
        for elt in __file__.split('/')[1:]:
            if elt in ['lib', 'lib32', 'lib64']:
                candidate = check_candidate(path, directory=directory)
                if candidate is not None:
                    return candidate
            path = os.path.join(path, elt)
    for path in ['/usr', '/usr/local', '/opt', '/opt/ivre']:
        candidate = check_candidate(path, directory=directory)
        if candidate is not None:
            return candidate

if GEOIP_PATH is None:
    GEOIP_PATH = guess_prefix('geoip')

if HONEYD_IVRE_SCRIPTS_PATH is None:
    HONEYD_IVRE_SCRIPTS_PATH = guess_prefix('honeyd')
