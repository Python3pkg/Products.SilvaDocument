from Products.Silva.silvaxml.xmlexport import theXMLExporter, VersionedContentProducer, SilvaBaseProducer
from sprout.saxext.html2sax import saxify
from Products.ParsedXML.DOM.Core import Node

SilvaDocumentNS = 'http://infrae.com/ns/silva_document'

def initializeXMLExportRegistry():
    """Here the actual content types are registered. Non-Silva-Core content
    types probably need to register themselves in in their product
    __init__.pies
    """
    from Products.SilvaDocument.Document import Document, DocumentVersion
    exporter = theXMLExporter
    exporter.registerNamespace('doc', SilvaDocumentNS)
    exporter.registerProducer(Document, DocumentProducer)
    exporter.registerProducer(DocumentVersion, DocumentVersionProducer)


class DocumentProducer(VersionedContentProducer):
    """Export a Silva Document object to XML.
    """
    def sax(self):
        self.startElement('document', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElement('document')

class DocumentVersionProducer(SilvaBaseProducer):
    """Export a version of a Silva Document object to XML.
    """
    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.metadata()
        node = self.context.content.documentElement
        self.sax_node(node)
        self.endElement('content')

    def sax_node(self, node):
        """Export child nodes of a (version of a) Silva Document to XML
        """
        attributes = {}
        if node.attributes:
            for key in node.attributes.keys():
                attributes[key] = node.attributes[key].value
        self.startElementNS(SilvaDocumentNS, node.nodeName, attributes)
        if node.nodeName == 'source':
            # XXX Eventually move this over to SilvaExternalSources
            from Products.SilvaExternalSources.ExternalSource import getSourceForId
            source = getSourceForId(self.context, attributes['id'])
            parameters = {}
            for child in node.childNodes:
                if child.nodeName == 'parameter':
                    text = ''
                    for grandChild in child.childNodes:
                        if grandChild.nodeType == Node.TEXT_NODE:
                            text = text + grandChild.nodeValue
                    parameters[child.attributes['key']] = text
            if self.getSettings().externalRendering():
                html = source.index_html(parameters)
                # XXX testing. Is this really enough? Suspiciously like magic...
                saxify(html, self.handler)
        elif node.hasChildNodes():
            for child in node.childNodes:
                if child.nodeType == Node.TEXT_NODE:
                    if child.nodeValue:
                        self.handler.characters(child.nodeValue)
                elif child.nodeType == Node.ELEMENT_NODE:
                    self.sax_node(child)
        else:
            if node.nodeValue:
                self.handler.characters(node.nodeValue)
        self.endElementNS(SilvaDocumentNS, node.nodeName)
