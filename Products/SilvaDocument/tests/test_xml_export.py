# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserverd.
# See also LICENSE.txt
# $Id$

import unittest

from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva.silvaxml import xmlexport
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase
from Products.SilvaDocument.testing import FunctionalLayer

from silva.core.references.interfaces import IReferenceService
from zope import component


class XMLExportTestCase(SilvaXMLTestCase):
    """Test Silva Document XML export.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Test <boo>Folder</boo>')
        factory = self.root.folder.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Test document')

    def test_document(self):
        document = self.root.folder.document
        version = document.get_editable()
        version.content = ParsedXML(
            'document',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
   <node foo="bar">承諾広告＊既に、２億、３億、５億９千万円収入者が続出<node2>boo</node2>baz</node>
</doc>""")

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_document.silvaxml', globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_document_link(self):
        """Try to export a document that links to other resources.
        """
        document = self.root.folder.document
        version = document.get_editable()
        version.content = ParsedXML(
            'document',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
   <p>
      This is a reference to
      <link target="_blank" reference="infrae-site" title="">Infrae</link>
   </p>
</doc>""")

        # Create a link that will be the target of our reference in our document
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'Link to Infrae', relative=False, url='http://infrae.com')
        service = component.getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"document link")
        reference.set_target(self.root.folder.link)
        reference.add_tag(u"infrae-site")

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_link.silvaxml', globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_document_image(self):
        """Try to export a document that use an image.
        """
        document = self.root.folder.document
        version = document.get_editable()
        version.content = ParsedXML(
            'document',
            """<?xml version="1.0" encoding="utf-8"?>
           <doc><p>Torvald last picture</p>
           <image reference="torvald-pic" alignment="" title="Torvald"></image>
           </doc>""")

        # Create a image to use in the document
        factory = self.root.folder.manage_addProduct['Silva']
        with self.layer.open_fixture('chocobo.jpg') as image:
            factory.manage_addImage('torvald', 'Torvald', image)
        service = component.getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"document link")
        reference.set_target(self.root.folder.torvald)
        reference.add_tag(u"torvald-pic")

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(xml, 'test_export_image.silvaxml', globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(
            info.getAssetPaths(), [(('', 'root', 'folder', 'torvald'), '1')])

    def test_document_with_source_export(self):
        self.layer.login('manager')
        factory = self.root.folder.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource(
            'codesource', 'A Code Source', 'script')

        # add a script to the code source
        factory = self.root.folder.codesource.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        script = self.root.folder.codesource.script
        script.write('return "<ul><li>Item 1</li><li>Item 2</li></ul>"')

        self.layer.login('author')

        doc = self.root.folder.document
        doc_edit = doc.get_editable()
        doc_edit.content = ParsedXML(
            'test_document',
            """<?xml version="1.0" encoding="utf-8"?><doc>
            <source id="codesource"></source>
            <p type="normal">This is some text.</p>
            </doc>""")

        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(
            xml, 'test_export_codesource.silvaxml', globals())
        # The code-source went into a ZEXP.
        self.assertEqual(
            info.getZexpPaths(),
            [(('', 'root', 'folder', 'codesource'), '1.zexp')])
        self.assertEqual(info.getAssetPaths(), [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLExportTestCase))
    return suite
