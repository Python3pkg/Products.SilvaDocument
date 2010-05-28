# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserverd.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.helpers import open_test_file
from Products.Silva.silvaxml import xmlimport


class ImportTestCase(unittest.TestCase):
    """Test the import of a document.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_document_import(self):
        importfolder = self.root.folder
        importer = xmlimport.theXMLImporter
        source_file = open_test_file('test_document.xml', globals(), 'r')
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        importer.importFromFile(
            source_file,
            result=importfolder,
            settings=test_settings,
            info=test_info)
        source_file.close()

        document_version = importfolder.testfolder.test_document.get_editable()
        self.assertEquals(
            document_version.get_title(),
            'This is (surprise!) a document')

        doc = document_version.content.documentElement.__str__()
        self.assertEquals(doc,
        u'<doc>\n            <p>\n            <em>\u627f\u8afe\u5e83\u544a\uff0a\u65e2\u306b\u3001\uff12\u5104\u3001\uff13\u5104\u3001\uff15\u5104\uff19\u5343\u4e07\u5186\u53ce\u5165\u8005\u304c\u7d9a\u51fa<strong>boo</strong>\n              baz</em>\n            </p>\n          </doc>')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImportTestCase))
    return suite
