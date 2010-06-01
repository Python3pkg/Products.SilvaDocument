# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserverd.
# See also LICENSE.txt
# $Id$

import unittest

from zope.component import getUtility

from Products.SilvaDocument.interfaces import IDocument
from Products.SilvaMetadata.interfaces import IMetadataService

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import open_test_file
from Products.Silva.tests.test_xmlimport import SilvaXMLTestCase
from Products.Silva.silvaxml import xmlimport


class XMLImportTestCase(SilvaXMLTestCase):
    """Test the import of a document.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.metadata = getUtility(IMetadataService)

    def test_document(self):
        """Import a simple document.
        """
        self.import_file('test_import_document.silvaxml', globals())
        self.assertListEqual(self.root.folder.objectIds(), ['folder'])
        self.assertListEqual(self.root.folder.folder.objectIds(), ['document'])

        document = self.root.folder.folder.document
        self.failUnless(IDocument.providedBy(document))

        version = document.get_editable()
        self.failIf(version is None)
        self.assertEqual(document.get_viewable(), None)
        self.assertEqual(version.get_title(), u'Previewing a document')

        binding = self.metadata.getMetadata(version)
        self.assertEqual(binding.get('silva-extra', 'creator'), u'wimbou')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'wimbou')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'), u'Previewing a document')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'How to click on preview.')
        self.assertEqual(
            binding.get('silva-extra', 'comment'),
            u'Caution: A special skill-set is required for this operation.')

        with open_test_file(
            'test_imported_document.docxml', globals()) as expected_document:
            self.assertXMLEqual(
                str(version.content.documentElement),
                expected_document.read())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite
