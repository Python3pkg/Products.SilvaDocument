# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.interfaces import ISilvaObject
from five import grok


class EmptyNotes(grok.View):

    grok.context(ISilvaObject)
    grok.name(u'markupnotes')
    grok.require('silva.ReadSilvaContent')

    def render(self):
        return u''

