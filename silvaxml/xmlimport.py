# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import uuid

from Products.Silva.silvaxml.xmlimport import (
    SilvaBaseHandler, NS_URI, updateVersionCount, resolve_path)
from Products.SilvaDocument.transform.base import LINK_REFERENCE_TAG

from zope.component import getUtility
from silva.core import conf as silvaconf
from silva.core.services.interfaces import ICataloging
from silva.core.references.interfaces import IReferenceService

DOC_NS_URI = 'http://infrae.com/namespace/silva-document'
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
            ICataloging(self.result()).reindex()


class DocumentVersionHandler(SilvaBaseHandler):

    def getOverrides(self):
        return {(DOC_NS_URI, 'doc'): DocXMLHandler, }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            uid = attrs[(None, 'version_id')].encode('utf-8')
            self.parent().manage_addProduct['SilvaDocument'].manage_addDocumentVersion(
                uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            updateVersionCount(self)
            self.setMaintitle()
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

    def link_attributes(self, attributes):
        if 'reference' in attributes:
            service = getUtility(IReferenceService)
            reference = service.new_reference(
                self.__version, name=LINK_REFERENCE_TAG)
            link_name = unicode(uuid.uuid1())
            reference.add_tag(link_name)
            info = self.getInfo()
            info.addAction(
                resolve_path,
                [reference.set_target, info.importRoot(), attributes['reference']])
            attributes['reference'] = link_name
        return attributes

    TAG_ATTRIBUTES = {'link': link_attributes}

    def startElementNS(self, name, qname, attrs):
        if name == (DOC_NS_URI, 'doc'):
            version = self.parent()
            self.__tree = version.content
            self.__current_node = self.__tree.documentElement
        else:
            child = self.__tree.createElement(name[1])

            # Collect attributes
            attributes = {}
            for ns, attr in attrs.keys():
                attributes[attr] = attrs[(ns,attr)]

            # Customize attributes
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
        if name == (DOC_NS_URI, 'doc'):
            self.__current_node = None
        else:
            self.__current_node = self.__current_node.parentNode
