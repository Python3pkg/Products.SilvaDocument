from zope.interface import implements

# zope imports
import zLOG

# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade
from Products.Silva.helpers import SwitchClass

from Products.SilvaDocument.Document import Document, DocumentVersion

class UpgradeDocumentXML:

    implements(IUpgrader)

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

def initialize():
    upgrade.registry.registerUpgrader(SwitchClass(Document),
        '0.9.3', Document.meta_type)
    upgrade.registry.registerUpgrader(SwitchClass(DocumentVersion,
        args=()), '0.9.3', DocumentVersion.meta_type)
    upgrade.registry.registerUpgrader(UpgradeDocumentXML(), '0.9.3',
        DocumentVersion.meta_type)

