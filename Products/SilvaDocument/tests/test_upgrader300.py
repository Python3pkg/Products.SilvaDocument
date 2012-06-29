
import unittest
from Products.SilvaDocument.testing import Functional30Layer
from Products.SilvaDocument.upgrader.upgrade_300 import document_upgrader
from silva.app.document.interfaces import IDocument, IDocumentVersion


class UpgraderTestCase(unittest.TestCase):
    layer = Functional30Layer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Information')

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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UpgraderTestCase))
    return suite

