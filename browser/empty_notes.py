# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.interfaces import ISilvaObject

from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf


class EmptyNotes(silvaviews.View):

    silvaconf.context(ISilvaObject)
    silvaconf.name(u'markupnotes')
    silvaconf.require('silva.ReadSilvaContent')

    def render(self):
        return u''

