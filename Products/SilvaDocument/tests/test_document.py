# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject

from Products.SilvaDocument.interfaces import IDocument, IDocumentVersion
from Products.SilvaDocument.testing import FunctionalLayer


class DocumentTestCase(unittest.TestCase):
    """Test a SilvaDocument
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')

    def test_interfaces(self):
        self.failUnless(verifyObject(IDocument, self.root.document))
        self.failUnless(verifyObject(
                IDocumentVersion, self.root.document.get_editable()))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentTestCase))
    return suite
