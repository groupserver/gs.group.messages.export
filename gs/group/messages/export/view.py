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
from json import dumps as dump_json
from logging import getLogger
log = getLogger('gs.group.messages.export')
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter
from gs.content.email.base import TextMixin
from gs.core import curr_time
from gs.group.base import GroupPage
from gs.group.list.email.text.post import Post
from .queries import PostsQuery


class PostsJSON(GroupPage):
    '''The list of posts in a given month, in JSON format'''

    @Lazy
    def yearMonth(self):
        default = curr_time().strftime('%Y%m')
        ym = self.request.get('month', default)
        if len(ym) != 6:
            ym = default
        year = int(ym[:4])
        month = int(ym[-2:])
        retval = (year, month)
        return retval

    @Lazy
    def query(self):
        retval = PostsQuery()
        return retval

    def __call__(self):
        year, month = self.yearMonth
        fn = b'{0}-{1}-posts-{2:4d}{3:02d}.json'.format(
            self.siteInfo.id, self.groupInfo.id, year, month)
        self.request.response.setHeader(b'Content-Disposition',
                                        b'inline; filename='+fn)
        self.request.response.setHeader(b'Content-type',
                                        b'application/json')

        posts = self.query.posts_for_month(self.siteInfo.id,
                                           self.groupInfo.id, year, month)
        retval = dump_json(posts)
        return retval


class MessageTraversal(GroupPage):
    '''The "traversal" system for the mbox view of a post

:param messages: The messages folder for a group.
:type messages: Products.XWFMailingListManager.interfaces.IGSMessagesFolder
:param request: The request-object.
'''
    def __init__(self, messages, request):
        super(MessageTraversal, self).__init__(messages, request)
        self.traverse_subpath = []
        self.post = None

    def publishTraverse(self, request, name):
        '''Traverse through the path

The first time this method is called it loads the post referenced by
``name``. Subsequent calls just append ``name`` to the ``traverse_subpath``
property.'''
        self.traverse_subpath.append(name)
        if self.post is None:
            # Load the post, and hook it into the aquisition tree
            self.post = Post(self.context, self.groupInfo, name)
        return self

    def __call__(self):
        '''The traversal is done, render something.

Get a named adapter for the post, and the request, defaulting to the
``mbox`` name. Call the adapter, returning the result.'''
        tsp = self.traverse_subpath
        name = tsp[1] if len(tsp) > 1 else 'mbox'
        page = getMultiAdapter((self.post, self.request),
                               name=name)
        retval = page()
        return retval


class GSMime(MIMENonMultipart):
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
        groupObj = self.context.context
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
        fn = b'{0}-{1}-post-{2}.mbox'.format(
            self.siteInfo.id, self.groupInfo.id, self.post['post_id'])
        self.request.response.setHeader(b'Content-Disposition',
                                        b'inline; filename='+fn)
        self.request.response.setHeader(b'Content-type',
                                        b'text/plain; charset=utf-8')

        m = self.post['header'] + '\n\nDiscarded'
        e = Parser().parsestr(m, headersonly=True)
        if 'Content-Transfer-Encoding' in e:
            del(e['Content-Transfer-Encoding'])

        outMsg = self.payload
        for h, v in e.items():
            if outMsg[h]:
                pass
            else:
                outMsg[h] = v
        dateStr = self.post['date'].strftime('%a, %d %b %Y %H:%M:%S %z')
        outMsg['Date'] = dateStr
        outMsg.set_unixfrom(self.unixfrom(e['from'], dateStr))

        retval = outMsg.as_string(unixfrom=True)
        return retval
