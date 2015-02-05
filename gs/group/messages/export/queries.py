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
#from operator import and_
import sqlalchemy as sa
#from datetime import datetime
#from pytz import UTC
#from zope.sqlalchemy import mark_changed
from gs.database import getSession, getTable


class PostsQuery(object):
    def __init__(self, context=None):
        self.postTable = getTable('post')
        self.hiddenPostTable = getTable('hidden_post')

    def posts_for_month(self, siteId, groupId, year, month):
        pt = self.postTable
        s = sa.select([pt.c.post_id], order_by=pt.c.date)
        s.append_whereclause(pt.c.site_id == siteId)
        s.append_whereclause(pt.c.group_id == groupId)
        s.append_whereclause(sa.extract('year', pt.c.date) == year)
        s.append_whereclause(sa.extract('month', pt.c.date) == month)

        session = getSession()
        r = session.execute(s)
        retval = [row['post_id'] for row in r]
        assert type(retval) == list
        return retval

    def months_with_posts(self, siteId, groupId):
        pt = self.postTable
        cols = [sa.extract('year', pt.c.date).label('year'),
                sa.extract('month', pt.c.date).label('month'),
                sa.func.count(pt.c.post_id).label('post_count'), ]
        s = sa.select(cols, order_by=[sa.desc('year'), sa.desc('month')],
                      group_by=['year', 'month'])
        s.append_whereclause(pt.c.site_id == siteId)
        s.append_whereclause(pt.c.group_id == groupId)

        session = getSession()
        r = session.execute(s)

        retval = [{'year': x['year'], 'month': x['month'],
                   'post_count': x['post_count']} for x in r]
        return retval
