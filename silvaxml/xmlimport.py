# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import uuid

from Products.Silva.silvaxml.xmlimport import (
    SilvaBaseHandler, NS_URI, updateVersionCount, resolve_path)
from Products.SilvaDocument.silvaxml import NS_SILVA_DOCUMENT
from Products.SilvaDocument.transform.base import LINK_REFERENCE_TAG

from zope.component import getUtility
from silva.core import conf as silvaconf
from silva.core.references.interfaces import IReferenceService

silvaconf.namespace(NS_URI)


class DocumentHandler(SilvaBaseHandler):
    silvaconf.name('document')

    def getOverrides(self):
        return {(NS_URI, 'content'): DocumentVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'document'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['SilvaDocument'].manage_addDocument(
                uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'document'):
            self.notifyImport()


class DocumentVersionHandler(SilvaBaseHandler):

    def getOverrides(self):
        return {(NS_SILVA_DOCUMENT, 'doc'): DocXMLHandler, }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            uid = attrs[(None, 'version_id')].encode('utf-8')
            self.parent().manage_addProduct['SilvaDocument'].manage_addDocumentVersion(
                uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            updateVersionCount(self)
            self.storeMetadata()
            self.storeWorkflow()


class DocXMLHandler(SilvaBaseHandler):
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
        info = self.getInfo()
        info.addAction(
            resolve_path, [reference.set_target, info.importRoot(), target])
        return reference_name

    def update_reference_attribute(self, attributes):
        if 'reference' in attributes:
            attributes['reference'] = self._new_reference(
                attributes['reference'])
        return attributes

    TAG_ATTRIBUTES = {'link': update_reference_attribute,
                      'image': update_reference_attribute}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_DOCUMENT, 'doc'):
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
        if name == (NS_SILVA_DOCUMENT, 'doc'):
            self.__current_node = None
        else:
            self.__current_node = self.__current_node.parentNode
