# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserverd.
# See also LICENSE.txt
# $Id$

import unittest

from zope.component import getUtility
from silva.core.interfaces.events import IContentImported
from silva.core.references.interfaces import IReferenceService
from silva.core.services.interfaces import ICatalogService

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from Products.SilvaDocument.interfaces import IDocument, IDocumentVersion
from Products.SilvaDocument.testing import FunctionalLayer
from Products.SilvaDocument.transform.base import LINK_REFERENCE_TAG


class XMLImportTestCase(SilvaXMLTestCase):
    """Test the import of a document.
    """
    layer = FunctionalLayer

    def assertDocumentEqual(self, version, filename, **replaces):
        """Assert that the content of the version is the same than the
        thing in the given file.
        """
        with self.layer.open_fixture(filename) as expected_source:
            expected = expected_source.read().format(**replaces)
            self.assertXMLEqual(
                unicode(version.content.documentElement), expected)

    def test_document(self):
        """Import a simple document.
        """
        self.import_file('test_import_document.silvaxml', globals())
        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/document'],
            IContentImported)
        self.assertItemsEqual(self.root.folder.objectIds(), ['document'])

        document = self.root.folder.document
        self.assertTrue(IDocument.providedBy(document))

        version = document.get_editable()
        self.assertFalse(version is None)
        self.assertTrue(IDocumentVersion.providedBy(version))
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
        self.assertDocumentEqual(version, 'test_imported_document.docxml')

        # Test the document have been indexed
        catalog = getUtility(ICatalogService)
        results = catalog(silvamaintitle=u"previewing document")
        self.assertItemsEqual(
            map(lambda r: r.getPath(), results),
            ['/root/folder/document',
             '/root/folder/document/0'])

    def test_document_link(self):
        """Try to import a document that contains a link.
        """
        self.import_file('test_import_link.silvaxml', globals())
        self.assertItemsEqual(
            self.root.folder.objectIds(), ['document', 'site'])

        document = self.root.folder.document
        link = self.root.folder.site
        self.assertTrue(IDocument.providedBy(document))

        version = document.get_viewable()
        self.assertFalse(version is None)
        self.assertTrue(IDocumentVersion.providedBy(version))
        self.assertEqual(document.get_editable(), None)
        self.assertEqual(version.get_title(), u'Cool site')

        service = getUtility(IReferenceService)
        # Hopefully there is only one link in the document so this
        # should match the only link we have
        reference = service.get_reference(version, LINK_REFERENCE_TAG)
        self.assertFalse(reference is None)
        self.assertItemsEqual(
            list(service.get_references_from(version)), [reference])
        self.assertEqual(reference.target, link)

        self.assertDocumentEqual(
            version, 'test_imported_link.docxml',
            link_reference=reference.tags[1])

        # Test the document have been indexed. It is published so we
        # can search on the fulltext.
        catalog = getUtility(ICatalogService)
        results = catalog(fulltext=u"übber-cool site")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].getObject(), version)

    def test_document_image(self):
        """Try to import a document that contains an image.
        """
        self.import_zip('test_import_image.zip', globals())
        self.assertItemsEqual(
            self.root.folder.objectIds(), ['document', 'pictures'])
        self.assertItemsEqual(
            self.root.folder.pictures.objectIds(), ['chocobo'])

        document = self.root.folder.document
        image = self.root.folder.pictures.chocobo
        self.assertTrue(IDocument.providedBy(document))

        version = document.get_viewable()
        self.assertFalse(version is None)
        self.assertTrue(IDocumentVersion.providedBy(version))
        self.assertEqual(document.get_editable(), None)
        self.assertEqual(version.get_title(), u'New picture shoots')

        service = getUtility(IReferenceService)
        # Hopefully there is only one image in the document so this
        # should match the only link we have
        reference = service.get_reference(version, LINK_REFERENCE_TAG)
        self.assertFalse(reference is None)
        self.assertItemsEqual(
            list(service.get_references_from(version)), [reference])
        self.assertEqual(reference.target, image)

        self.assertDocumentEqual(
            version, 'test_imported_image.docxml',
            image_reference=reference.tags[1])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite
