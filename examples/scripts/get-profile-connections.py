#!/usr/bin/env python
###
# (C) Copyright (2012-2016) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import range
from future import standard_library
standard_library.install_aliases()
import sys

PYTHON_VERSION = sys.version_info[:3]
PY2 = (PYTHON_VERSION[0] == 2)
if PY2:
    if PYTHON_VERSION < (2, 7, 9):
        raise Exception('Must use Python 2.7.9 or later')
elif PYTHON_VERSION < (3, 4):
    raise Exception('Must use Python 3.4 or later')

import hpOneView as hpov
from pprint import pprint


def acceptEULA(con):
    # See if we need to accept the EULA before we try to log in
    con.get_eula_status()
    try:
        if con.get_eula_status() is True:
            print('EULA display needed')
            con.set_eula('no')
    except Exception as e:
        print('EXCEPTION:')
        print(e)


def login(con, credential):
    # Login with given credentials
    try:
        con.login(credential)
    except:
        print('Login failed')


def output(con, name, profile, report):
    if report:
        print('\n{0:25}   {1:3}   {2:9}   {3:12}   {4:25}   {5:17}   {6:23}   {7:8}'.format('serverProfile', 'cid', 'portId', 'functionType', 'Network', 'mac', 'wwpn', 'boot'))
        print('{0:25}   {1:3}   {2:9}   {3:12}   {4:25}   {5:17}   {6:23}   {7:8}'.format('-------------', '---', '------', '------------', '-------', '---', '----', '----'))
        for conn in profile:
            network =  con.get_by_uri(conn['networkUri'])
            wwpn = conn['wwpn'] if conn['wwpn'] else ''
            boot = conn['boot']['priority'] if conn['boot']['priority'] else '' # boot priority can be null
            print('{0:25}   {1:3}   {2:9}   {3:12}   {4:25}   {5:17}   {6:23}   {7:8}'.format(name, conn['id'], conn['portId'], conn['functionType'], network['name'], conn['mac'], wwpn, boot))
    else:
        for conn in profile:
            print(('\nGetting Profile Connections List for Profile %s' % name))
            pprint(conn)

'''
Get a server profile's connection information.  If no profile name is supplied
connection information will be returned for all server profiles.
'''
def get_profile_connections_list(con, srv, name, report):
    for profile in srv.get_server_profiles():
        if profile['connections']:
            if name:
                if profile['name'] == name:
                    output(con, profile['name'], profile['connections'], report)
            else:
                output(con, profile['name'], profile['connections'], report)


def main():
    parser = argparse.ArgumentParser(add_help=True,
                        formatter_class=argparse.RawTextHelpFormatter,
                                     description='''
    Display Server Profile Connections

    Usage: ''')
    parser.add_argument('-a', dest='host', required=True,
                        help='''
    HP OneView Appliance hostname or IP address''')
    parser.add_argument('-u', dest='user', required=False,
                        default='Administrator',
                        help='''
    HP OneView Username''')
    parser.add_argument('-p', dest='passwd', required=True,
                        help='''
    HP OneView Password''')
    parser.add_argument('-c', dest='cert', required=False,
                        help='''
    Trusted SSL Certificate Bundle in PEM (Base64 Encoded DER) Format''')
    parser.add_argument('-y', dest='proxy', required=False,
                        help='''
    Proxy (host:port format''')
    parser.add_argument('-r', dest='report',
                        required=False, action='store_true',
                        help='''
    Format the output using a human readable report format''')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', dest='name',
                       help='''
    Name of the server profile to get''')
    group.add_argument('-g', dest='get_all',
                       action='store_true',
                       help='''
    Get ALL server profiles and exit''')

    args = parser.parse_args()
    credential = {'userName': args.user, 'password': args.passwd}

    con = hpov.connection(args.host)
    srv = hpov.servers(con)
    net = hpov.networking(con)
    sts = hpov.settings(con)

    if args.proxy:
        con.set_proxy(args.proxy.split(':')[0], args.proxy.split(':')[1])
    if args.cert:
        con.set_trusted_ssl_bundle(args.cert)

    login(con, credential)
    acceptEULA(con)

    # get a server profile's connection information
    get_profile_connections_list(con, srv, '', args.report)

if __name__ == '__main__':
    import sys
    import argparse
    sys.exit(main())

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
