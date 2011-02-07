# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from Products.SilvaDocument.interfaces import IDocument, IDocumentVersion
from Products.Silva.adapters.indexable import IndexableAdapter
from silva.core.interfaces.adapters import IIndexable


class DocumentIndexableAdapter(IndexableAdapter):

    grok.context(IDocument)

    def getIndexes(self):
        version = self.context.get_viewable()
        if version:
            return IIndexable(version).getIndexes()
        return []


class DocumentVersionIndexableAdapter(IndexableAdapter):

    grok.context(IDocumentVersion)

    def getIndexes(self):
        indexes = []
        docElement = self.context.content.firstChild
        nodes = docElement.getElementsByTagName('index')
        for node in nodes:
            indexTitle = node.getAttribute('title')
            if indexTitle:
                indexName = node.getAttribute('name')
                indexes.append((indexName, indexTitle))
        return indexes
