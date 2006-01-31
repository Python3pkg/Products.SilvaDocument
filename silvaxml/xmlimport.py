from Products.Silva.silvaxml.xmlimport import theXMLImporter, SilvaBaseHandler, NS_URI, generateUniqueId, updateVersionCount
from Products.SilvaDocument.Document import Document, DocumentVersion
from Products.Silva import mangle

DOC_NS_URI = 'http://infrae.com/ns/silva_document'

def initializeXMLImportRegistry():
    """Initialize the global importer object.
    """
    importer = theXMLImporter
    importer.registerHandler((NS_URI, 'document'), DocumentHandler)

class DocumentHandler(SilvaBaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'content'): DocumentContentHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'document'):
            id = attrs[(None, 'id')].encode('utf-8')
            uid = self.generateOrReplaceId(id)
            object = Document(uid)
            self.parent()._setObject(uid, object)
            self.setResult(getattr(self._parent, uid))

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'document'):
            self.result().indexVersions()
        
class DocumentContentHandler(SilvaBaseHandler):
    def getOverrides(self):
        return{
            (DOC_NS_URI, 'doc'): DocElementHandler,
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            id = attrs[(None, 'version_id')].encode('utf-8')
            if not mangle.Id(self._parent, id).isValid():
                return
            version = DocumentVersion(id, '')
            self.parent()._setObject(id, version)
            self.setResult(getattr(self._parent, id))
            updateVersionCount(self)
            
    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            self.setMaintitle()
            self.storeMetadata()
            self.storeWorkflow()
        
class DocElementHandler(SilvaBaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (DOC_NS_URI, 'doc'):
            self._node = self._parent.content.documentElement
            self._tree = self._parent.content
        else:
            child = self._tree.createElement(name[1])
            self._node.appendChild(child)
            self._node = child
        for ns, attr in attrs.keys():
            self._node.setAttribute(attr, attrs[(ns, attr)])
            
    def characters(self, chrs):
        textNode = self._tree.createTextNode(chrs)
        self._node.appendChild(textNode)

    def endElementNS(self, name, qname):
        if name == (DOC_NS_URI, 'doc'):
            self._node = None
        else:
            self._node = self._node.parentNode

def generateUniqueId(org_id, context):
        i = 0
        id = org_id
        ids = context.objectIds()
        while id in ids:
            i += 1
            add = ''
            if i > 1:
                add = str(i)
            id = 'import%s_of_%s' % (add, org_id)
        return id            
