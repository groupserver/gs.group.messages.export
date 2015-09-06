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
from datetime import date
from json import dumps as dump_json
from logging import getLogger
log = getLogger('gs.group.messages.export')
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter
from gs.core import curr_time
from gs.group.base import GroupPage
from gs.group.list.email.base import Post
from .queries import PostsQuery


class Export(GroupPage):
    'Export posts from a group'

    @Lazy
    def query(self):
        retval = PostsQuery()
        return retval

    @Lazy
    def months(self):
        retval = self.query.months_with_posts(self.siteInfo.id,
                                              self.groupInfo.id)
        for r in retval:
            r['year'] = int(r['year'])
            r['month'] = int(r['month'])
            r['date'] = date(r['year'], r['month'], 1)
        return retval


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
