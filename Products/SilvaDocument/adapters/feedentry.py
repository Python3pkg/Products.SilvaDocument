# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

import re
from silva.core.interfaces.adapters import IFeedEntry
from Products.SilvaDocument.interfaces import IDocument

class DocumentFeedEntryAdapter(grok.Adapter):
    """Adapter for Silva Documents to get an atom/rss feed entry
    representation."""

    grok.context(IDocument)
    grok.implements(IFeedEntry)

    def __init__(self, context):
        self.context = context
        self.version = self.context.get_viewable()
        self.ms = self.context.service_metadata

    def id(self):
        return self.url()

    def title(self):
        return self.context.get_title()

    def html_description(self):
        return ''
        document_element = self.version.content.documentElement
        ps = document_element.getElementsByTagName('p')
        if not ps:
            return ''
        p = ps[0]
        self.context.service_editor.setViewer('service_doc_viewer')
        self.context.REQUEST.other['model'] = self.version
        rendered = self.context.service_editor.renderView(p)
        del self.context.REQUEST.other['model']
        return rendered

    def description(self):
        return re.sub('<[^>]*>(?i)(?m)', ' ', self.html_description())

    def url(self):
        return self.context.absolute_url()

    def authors(self):
        authors = []
        creator = self.ms.getMetadataValue(self.context, 'silva-extra', 'creator')
        if creator != 'unknown':
            authors.append(creator)
        lastauthor = self.ms.getMetadataValue(
            self.context, 'silva-extra', 'lastauthor')
        if lastauthor != creator and lastauthor != 'unknown':
            authors.append(lastauthor)
        return authors

    def date_updated(self):
        return self.ms.getMetadataValue(
            self.version, 'silva-extra', 'publicationtime')

    def date_published(self):
        return self.context.get_first_publication_date()

    def keywords(self):
        return [self.subject()] + [
            kw.strip() for kw in self.ms.getMetadataValue(
                self.context, 'silva-extra', 'keywords').split(',')]

    def subject(self):
        return self.ms.getMetadataValue(
            self.context, 'silva-extra', 'subject')
