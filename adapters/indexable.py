# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from grokcore import component

from Products.SilvaDocument.interfaces import IDocument, IDocumentVersion
from Products.Silva.adapters.indexable import IndexableAdapter
from silva.core.conf.interfaces.adapters import IIndexable

class DocumentIndexableAdapter(IndexableAdapter):

    component.context(IDocument)

    def getIndexes(self):
        version = self.context.get_viewable()
        if version:
            return IIndexable(version).getIndexes()
        return []

class DocumentVersionIndexableAdapter(IndexableAdapter):

    component.context(IDocumentVersion)

    def getIndexes(self):
        version = self.context
        if version is None:
            return []
        indexes = []
        docElement = version.content.firstChild
        nodes = docElement.getElementsByTagName('index')
        for node in nodes:
            indexTitle = node.getAttribute('title')
            if indexTitle:
                indexName = node.getAttribute('name')
                indexes.append((indexName, indexTitle))
        return indexes
