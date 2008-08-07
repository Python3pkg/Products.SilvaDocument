# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from zope.interface import implements

# Silva
from Products.Silva.helpers import SwitchClass
from Products.Silva.upgrade import BaseUpgrader
from Products.SilvaDocument.Document import Document, DocumentVersion

class UpgradeDocumentXML(BaseUpgrader):

    def upgrade(self, obj):
        # <index name="foo">bar</index> to
        # <index name="foo"/>bar
        dom = obj.content
        self._upgrade_helper(dom.documentElement)
        return obj

    def _upgrade_helper(self, node):
        if node.nodeType == node.ELEMENT_NODE and node.nodeName == 'index':
            if node.nextSibling:
                while node.hasChildNodes():
                    node.parentNode.insertBefore(node.lastChild, node.nextSibling)
            else:
                while node.hasChildNodes():
                    node.parentNode.appendChild(node.firstChild)
        else:
            for child in node.childNodes:
                self._upgrade_helper(child)

upgradeDocumentXML = UpgradeDocumentXML('0.9.3', 'Silva Document')

class SwitchClassUpgrader(BaseUpgrader, SwitchClass):

    def __init__(self, version, meta_type, new_class):
        BaseUpgrader.__init__(self, version, meta_type)
        SwitchClass.__init__(self, new_class)
        

switchDocumentClass = SwitchClassUpgrader('0.9.3', 'Silva Document',  Document)
switchDocumentVersionClass = SwitchClassUpgrader('0.9.3', 'Silva Document Version', DocumentVersion)


