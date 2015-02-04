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
