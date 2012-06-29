
import unittest
from Products.SilvaDocument.testing import Functional30Layer
from Products.SilvaDocument.upgrader.upgrade_300 import document_upgrader
from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.core.interfaces import IOrderManager
from silva.core.layout.interfaces import IMarkManager
from silva.core.views.interfaces import IDisableBreadcrumbTag


class UpgraderTestCase(unittest.TestCase):
    layer = Functional30Layer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Information')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_upgrade_empty(self):
        """Upgrade a simple empty document.
        """
        document = self.root.document
        self.assertFalse(IDocument.providedBy(document))
        self.assertNotEqual(document.get_editable(), None)
        self.assertFalse(IDocumentVersion.providedBy(document.get_editable()))
        self.assertEqual(document.get_editable().get_title(), 'Information')
        self.assertEqual(document.get_viewable(), None)
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertNotEqual(upgraded.get_editable(), None)
        self.assertTrue(IDocumentVersion.providedBy(upgraded.get_editable()))
        self.assertEqual(document.get_editable().get_title(), 'Information')
        self.assertEqual(upgraded.get_viewable(), None)
        self.assertEqual(document_upgrader.validate(upgraded), False)

    def test_upgrade_customization_markers(self):
        """Upgrade a document with a marker.
        """
        document = self.root.document
        IMarkManager(document).add_marker(IDisableBreadcrumbTag)
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertIn(IDisableBreadcrumbTag, IMarkManager(upgraded).usedMarkers)

    def test_upgrade_container_order(self):
        """Upgrade a document keep its position.
        """
        document = self.root.document
        order = IOrderManager(self.root)
        self.assertEqual(order.get_position(document), 0)
        self.assertEqual(order.get_position(self.root.folder), 1)
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        order = IOrderManager(self.root)
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertEqual(order.get_position(upgraded), 0)
        self.assertEqual(order.get_position(self.root.folder), 1)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UpgraderTestCase))
    return suite

