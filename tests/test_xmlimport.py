# -*- coding: utf-8 -*-
import os, sys
import xml.sax
from xml.sax.handler import feature_namespaces
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

import unittest
    
from Products.Silva.tests import SilvaTestCase
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.silvaxml import xmlimport 

def testopen(path, rw):
    directory = os.path.dirname(__file__)
    return open(os.path.join(directory, path), rw)

class SetTestCase(SilvaTestCase.SilvaTestCase):
    def test_document_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        importer = xmlimport.theXMLImporter
        source_file = testopen('data/test_document.xml', 'r')
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
            'This is (surprise!) a document'
            )
        metadata_service = self.root.service_metadata
        binding = metadata_service.getMetadata(document_version)
        self.assertEquals(
           binding._getData('silva-extra').data['location'],
            'http://nohost/root/testfolder/test_document')
        doc = document_version.content.documentElement.__str__()
        self.assertEquals(doc,
        u'<doc>\n            <p>\n            <em>\u627f\u8afe\u5e83\u544a\uff0a\u65e2\u306b\u3001\uff12\u5104\u3001\uff13\u5104\u3001\uff15\u5104\uff19\u5343\u4e07\u5186\u53ce\u5165\u8005\u304c\u7d9a\u51fa<strong>boo</strong>\n              baz</em>\n            </p>\n          </doc>')
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite    
