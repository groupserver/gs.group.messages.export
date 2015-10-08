# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2015 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals, print_function
from email import encoders
from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr
from zope.cachedescriptors.property import Lazy
from gs.content.email.base import TextMixin
from gs.group.base import GroupPage


class GSMime(MIMENonMultipart):
    '''A generic attachment'''
    def __init__(self, _data, _type, _subtype,
                 _encoder=encoders.encode_base64, **_params):
        MIMENonMultipart.__init__(self, _type, _subtype, **_params)
        self.set_payload(_data)
        _encoder(self)


class MBox(GroupPage, TextMixin):
    @Lazy
    def post(self):
        return self.context.post

    @Lazy
    def bodyPayload(self):
        retval = MIMEMultipart('alternative')
        t = MIMEText(self.post['body'], 'plain', 'utf-8')
        retval.attach(t)
        if self.post['htmlbody']:
            h = MIMEText(self.post['htmlbody'], 'html', 'utf-8')
            retval.attach(h)
        return retval

    @Lazy
    def fileArchive(self):
        # The aquisition hierarachy:
        # MBox (self) / Post / Traversal / Messages / Group
        groupObj = self.aq_parent.aq_parent.aq_parent.aq_parent
        retval = getattr(groupObj, 'files')
        return retval

    @Lazy
    def payload(self):
        if self.post['has_attachments']:
            retval = MIMEMultipart('mixed')
            retval.attach(self.bodyPayload)
            for f in self.post['files_metadata']:
                mainType, subtype = f['mime_type'].split('/')
                data = self.fileArchive.get_file_by_id(f['file_id'])
                if data:
                    binaryData = str(data)
                    m = GSMime(binaryData, mainType, subtype,
                               filename=f['file_name'])
                    retval.attach(m)
        else:
            retval = self.bodyPayload
        return retval

    @staticmethod
    def unixfrom(fromHdr, date):
        fromAddr = parseaddr(fromHdr)[1]
        r = 'From {0} {1}'
        retval = r.format(fromAddr, date)
        return retval

    def __call__(self):
        self.set_header('post-{0}.mbox'.format(self.post['post_id']))

        m = self.post['header'] + '\n\nDiscarded'
        e = Parser().parsestr(m, headersonly=True)
        if 'Content-Transfer-Encoding' in e:
            del(e['Content-Transfer-Encoding'])

        outMsg = self.payload
        for h, v in e.items():
            if not outMsg[h]:
                outMsg[h] = v
        dateStr = self.post['date'].strftime('%a, %d %b %Y %H:%M:%S %z')
        outMsg['Date'] = dateStr
        outMsg.set_unixfrom(self.unixfrom(e['from'], dateStr))

        retval = outMsg.as_string(unixfrom=True)
        return retval
