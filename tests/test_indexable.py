# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import os.path

from zope.interface.verify import verifyObject
from silva.core.interfaces.adapters import IIndexable

from Products.Silva.tests import SilvaTestCase
from Products.Silva.tests.helpers import publishObject
from Products.Silva.silvaxml import xmlimport


def testdata_open(path):
    directory = os.path.dirname(__file__)
    return open(os.path.join(directory, 'data', path), 'r')


class IndexableTest(SilvaTestCase.SilvaTestCase):
    """Test the Indexer support of SilvaDocument.
    """

    def test_empty_document(self):
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('doc', 'Document')
        doc = self.root.doc

        indexable = IIndexable(doc)
        self.failUnless(verifyObject(IIndexable, indexable))
        self.assertEqual(indexable.getIndexes(), [])

        publishObject(doc)
        indexable = IIndexable(doc)
        self.failUnless(verifyObject(IIndexable, indexable))
        self.assertEqual(indexable.getIndexes(), [])

    def test_not_empty_document(self):
        # XML import is the only way to get a document ...
        importer = xmlimport.theXMLImporter
        source_file = testdata_open('test_indexable.xml')
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

        publishObject(doc)
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
