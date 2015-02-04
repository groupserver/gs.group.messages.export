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
from __future__ import absolute_import, unicode_literals
from json import dumps as dump_json
from logging import getLogger
log = getLogger('gs.group.messages.export')
from zope.cachedescriptors.property import Lazy
from gs.core import curr_time
from gs.group.base import GroupPage
from .queries import PostsQuery


class PostsJSON(GroupPage):

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
        posts = self.query.posts_for_month(self.siteInfo.id,
                                           self.groupInfo.id, year, month)
        retval = dump_json(posts)
        return retval
