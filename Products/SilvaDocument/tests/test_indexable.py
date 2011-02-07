# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces.adapters import IIndexable
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import publish_object, open_test_file
from Products.Silva.silvaxml import xmlimport


class IndexableTest(unittest.TestCase):
    """Test the Indexer support of SilvaDocument.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_empty_document(self):
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('doc', 'Document')
        doc = self.root.doc

        indexable = IIndexable(doc)
        self.failUnless(verifyObject(IIndexable, indexable))
        self.assertEqual(indexable.getIndexes(), [])

        publish_object(doc)
        indexable = IIndexable(doc)
        self.failUnless(verifyObject(IIndexable, indexable))
        self.assertEqual(indexable.getIndexes(), [])

    def test_not_empty_document(self):
        # XML import is the only way to get a document ...
        importer = xmlimport.theXMLImporter
        source_file = open_test_file('test_indexable.xml', globals())
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        importer.importFromFile(
            source_file,
            result=self.root,
            settings=test_settings,
            info=test_info)
        source_file.close()
        doc = self.root.content_types

        indexable = IIndexable(doc)
        self.failUnless(verifyObject(IIndexable, indexable))
        self.assertEqual(indexable.getIndexes(), [])

        publish_object(doc)
        indexable = IIndexable(doc)
        self.failUnless(verifyObject(IIndexable, indexable))
        self.assertEqual(
            indexable.getIndexes(),
            [(u'Document', u'Document'), (u'Folder', u'Folder'),
             (u'Publication', u'Publication'), (u'Image', u'Image'),
             (u'File', u'File'), (u'Find', u'Find'), (u'Ghost', u'Ghost'),
             (u'Ghost_Folder', u'Ghost Folder'),
             (u'Indexer', u'Indexer'), (u'Link', u'Link'),
             (u'Automatic_Table_of_Contents', u'Automatic Table of Contents'),
             (u'AutoTOC', u'AutoTOC'), (u'CSV_Source', u'CSV Source')])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexableTest))
    return suite
