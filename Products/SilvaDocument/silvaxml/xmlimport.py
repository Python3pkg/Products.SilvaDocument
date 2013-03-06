# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import uuid

from Products.SilvaDocument.silvaxml import NS_DOCUMENT_URI
from Products.SilvaDocument.transform.base import LINK_REFERENCE_TAG

from zope.component import getUtility
from silva.core.xml import handlers, NS_SILVA_URI
from silva.core import conf as silvaconf
from silva.core.references.interfaces import IReferenceService

silvaconf.namespace(NS_SILVA_URI)


class DocumentHandler(handlers.SilvaHandler):
    silvaconf.name('document')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): DocumentVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'document'):
            uid = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['SilvaDocument']
            factory.manage_addDocument(uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'document'):
            self.notifyImport()


class DocumentVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {(NS_DOCUMENT_URI, 'doc'): DocXMLHandler, }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            uid = attrs[(None, 'version_id')].encode('utf-8')
            factory = self.parent().manage_addProduct['SilvaDocument']
            factory.manage_addDocumentVersion(uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class DocXMLHandler(handlers.SilvaHandler):
    """Import and convert Silva Document XML.
    """

    def __init__(self, *args, **kwargs):
        super(DocXMLHandler, self).__init__(*args, **kwargs)
        self.__tree = None
        self.__current_node = None
        self.__version = self.parent()

    def _new_reference(self, target):
        """Create a new reference for link/image
        """
        service = getUtility(IReferenceService)
        reference = service.new_reference(
            self.__version, name=LINK_REFERENCE_TAG)
        reference_name = unicode(uuid.uuid1())
        reference.add_tag(reference_name)
        importer = self.getExtra()
        importer.resolveImportedPath(
            self.__version, reference.set_target, target)
        return reference_name

    def update_reference_attribute(self, attributes):
        if 'reference' in attributes:
            attributes['reference'] = self._new_reference(
                attributes['reference'])
        return attributes

    TAG_ATTRIBUTES = {'link': update_reference_attribute,
                      'image': update_reference_attribute}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_DOCUMENT_URI, 'doc'):
            version = self.parent()
            self.__tree = version.content
            self.__current_node = self.__tree.documentElement
        else:
            child = self.__tree.createElement(name[1])

            # Collect attributes
            attributes = {}
            for ns, attr in attrs.keys():
                attributes[attr] = attrs[(ns,attr)]

            # Update attributes
            if name[1] in self.TAG_ATTRIBUTES:
                self.TAG_ATTRIBUTES[name[1]](self, attributes)

            # Create node
            self.__current_node.appendChild(child)
            self.__current_node = child
            for name, value in attributes.items():
                self.__current_node.setAttribute(name, value)

    def characters(self, chrs):
        textNode = self.__tree.createTextNode(chrs)
        self.__current_node.appendChild(textNode)

    def endElementNS(self, name, qname):
        if name == (NS_DOCUMENT_URI, 'doc'):
            self.__current_node = None
        else:
            self.__current_node = self.__current_node.parentNode
