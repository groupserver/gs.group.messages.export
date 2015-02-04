============================
``gs.group.messages.export``
============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Export messages from a GroupServer group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2015-03-04
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.Net`_.

.. _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

Introduction
============

This product provides the pages used to export messages from a
GroupServer_ group. This module supplies a page_ to provide a
user interface, JavaScript_ to download the posts, and an `mbox
view`_ of a post.

Page
====

The page ``export.html`` (in the context of the ``messages``
folder of a group) provides links to download all the posts in a
single month as an ``mbox`` file. The posts are provided on a
month-by-month basis so the administrator can regularly update
the off-site archive of messages.

The ``gs-group-messages-export-posts.json`` view (in the
``messages`` context) provides a list of post-identifiers in JSON
format. The month is specified using the ``month`` query-string;
the current month is returned if no query-string is provided.

The posts are downloaded by the JavaScript_ that assembles the
posts into a single ``mbox`` file.

JavaScript
==========

The JavaScript ``gs-group-messages-export-20150210.js`` gets a
list of posts, and then downloads the `mbox view`_ of each post,
finally assembling the posts into an mbox file.

``mbox`` view
=============

The mbox view of a post is provided by the
``gs-group-messages-export-mbox`` traversal in the ``messages``
context. It assembles a complete email message from the

* Plain-text body,
* HTML body,
* The stored headers, and
* The stored files.

The returned message is **different** from what was received:
some information is discarded when GroupServer processes a
message (see `the message storage product`_ for more
information).

Resources
=========

- Code repository: https://github.com/groupserver/gs.group.messages.export
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _the message storage product: https://github.com/groupserver/gs.group.list.store

..  LocalWords:  groupserver Organization mbox html json
