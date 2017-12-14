#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses
#
# Usage: python encrypt.py [options] DLC-file
#
# Offene Implementierung einer DLC Decryption. DLC (Download Link Container)
# basiert auf einer server-seitigen Verschlüsselung, d.h. es ist unmgöglich,
# einen Container lokal zu entschlüsseln. Vom jDownloader-Team werden API-Keys
# an alternative Download-Manager ausgegeben, die notfalls geblacklistet
# werden können, sofern ein Missbrauch (massenhafte Entschlüsslung zum Melden
# von Links) vorliegt.

# TODO: app-key requires a different destType in API, needs researching
#
# rsdc, load

import sys; reload(sys); sys.setdefaultencoding('utf-8')
import base64
import urllib2

from cgi import escape
from HTMLParser import HTMLParser

from Crypto.Cipher import AES


class Debase(HTMLParser):
    """DLC contains kinda XML, but every TEXT and ATTRIBUTE nodes are
    obfuscated (I can not explain why) using base64.standard_b64decode"""
    
    def __init__(self, html):
        HTMLParser.__init__(self)
        self.result = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if attrs:
            self.result.append('<%s %s>' % (tag, ' '.join(
                ['%s="%s"' % (k, escape(base64.standard_b64decode(v))) for k,v in attrs])))
        else:
             self.result.append('<%s>' % tag)

    def handle_data(self, data):
        self.result.append(escape(base64.standard_b64decode(data).decode('utf-8', 'replace')))
    
    def handle_endtag(self, tag):
        self.result.append('</%s>' % tag)

def decrypt(dlc, key, iv, name):
    """encrypts data in dlc. Based on pyload's
    pyload/module/plugins/container/DLC_27.pyc. Requires an active internet
    connection and is limited to a maximum API-calls per hour per IP."""
    
    api = 'http://service.jdownloader.org/dlcrypt/service.php?srcType=dlc&destType=%s&data=%s'
    urlopen = urllib2.build_opener()
    urlopen.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:5.0.1) Gecko/20100101 Firefox/5.0.1'),
                          ("Accept", "*/*"),
                          ("Accept-Language", "en-US,en"),
                          ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"),
                          ("Connection", "keep-alive"),
                          ("Keep-Alive", "300")]
                          
    aes = AES.new(key, AES.MODE_CBC, iv)
    
    dlckey = dlc[(-88):]
    dlcdata = base64.standard_b64decode(dlc[:(-88)])
    data = urlopen.open(api % (name, dlckey)).read()
    rc = data.replace('<rc>', '').replace('</rc>', '')
    
    dlckey = aes.decrypt(base64.standard_b64decode(rc))
    aes = AES.new(dlckey, AES.MODE_CBC, dlckey)
    return base64.standard_b64decode(aes.decrypt(dlcdata))
    
if __name__ == '__main__':
    
    from optparse import OptionParser, make_option
    
    options = [
        make_option('-k', '--key', dest='key', metavar='str',
                    help="application key"),
        make_option('-v', '--iv', dest='iv', metavar='str',
                    help="application's IV"),
        make_option('-n', '--name', dest='name', metavar='str',
                    help="application name, e.g. %s" % ', '.join(['pylo', 'load', 'rsdc'])),
        make_option('-i', '--introspect', dest='introspect', action='store_true',
            default=False, help="print whole XML"),
        make_option('-d', '--dont-decrypt', dest='decrypt', action='store_false',
            default=True, help="do not decrypt XML, only works with '-i'"),
    ]
    
    descr = ("dlc.py is a small script to decrypt DLC files. It requires a "
            "valid application key. Currently, it is based on pyload.")
    
    parser = OptionParser(option_list=options, description=descr,
        usage="usage: %prog [options] FILE")
    options, args = parser.parse_args()
    
    if len(args) != 1:
        parser.print_usage()
        sys.exit(2)
        
    if not options.key or not options.iv:
        print >> sys.stderr, '[error]: dlc.py can not provide any key/iv in plaintext'
        sys.exit(2)
        
    try:
        dlc = open(args[0]).read()
    except OSError:
        print 'unable to open %s' % args[0]
        sys.exit(1)
        
    data = decrypt(dlc.strip(), key=options.key, iv=options.iv, name=options.name)
    
    if options.introspect:
        from lxml import etree
        if options.decrypt:
            r = etree.fromstring(''.join(Debase(data).result))
            print etree.tostring(r, pretty_print=True)
        else:
            r = etree.fromstring(data)
            print etree.tostring(r, pretty_print=True)
    else:
        from xml.etree.ElementTree import fromstring
        el = fromstring(''.join(Debase(data).result))
        for item in el.getiterator('file'):
            print item.find('url').text