# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from Products.SilvaDocument.interfaces import IDocument
from Products.Silva.adapters.indexable import IndexableAdapter


class DocumentIndexableAdapter(IndexableAdapter):
    grok.context(IDocument)

    def get_entries(self):
        version = self.context.get_viewable()
        if version:
            indexes = []
            docElement = version.content.firstChild
            nodes = docElement.getElementsByTagName('index')
            for node in nodes:
                indexTitle = node.getAttribute('title')
                if indexTitle:
                    indexName = node.getAttribute('name')
                    indexes.append((indexName, indexTitle))
            return indexes
        return []
