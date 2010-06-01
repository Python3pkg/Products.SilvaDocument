# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.silvaxml.xmlimport import (
    SilvaBaseHandler, NS_URI, updateVersionCount)
from Products.Silva import mangle

from silva.core import conf as silvaconf
from silva.core.services.interfaces import ICataloging

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
        return {(DOC_NS_URI, 'doc'): DocElementHandler, }

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


class DocElementHandler(SilvaBaseHandler):

    def startElementNS(self, name, qname, attrs):
        if name == (DOC_NS_URI, 'doc'):
            version = self.parent()
            self._tree = version.content
            self._node = self._tree.documentElement
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
