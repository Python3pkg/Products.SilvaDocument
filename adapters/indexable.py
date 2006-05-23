from Products.Silva.adapters.indexable import IndexableAdapter
from Products.Silva.adapters import interfaces

class DocumentIndexableAdapter(IndexableAdapter):
    def getIndexes(self):
        version = self.context.get_viewable()
        return interfaces.IIndexable(version).getIndexes()

class DocumentVersionIndexableAdapter(IndexableAdapter):
    def getIndexes(self):
        version = self.context
        if version is None:
            return []
        indexes = []
        docElement = version.content.firstChild
        nodes = docElement.getElementsByTagName('index')
        for node in nodes:
            indexName = node.getAttribute('name')
            indexes.append(indexName)
        return indexes        