# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import TestCase, TestRequest
from Products.SilvaDocument.Document import DocumentHTML
from Products.SilvaDocument.testing import FunctionalLayer


class XSLTRenderingTestCase(TestCase):
    """Test XSLT rendering.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        self.request = TestRequest()
        self.version = self.root.document.get_editable()

    def set_document_xml(self, source_filename):
        """Set the document xml from the content of the source file.
        """
        with self.layer.open_fixture(source_filename) as source:
            self.version.content.manage_edit(source.read())

    def assertRenderingEqual(self, expected_filename):
        """Verify that the rendering of the document match the content
        of the given filename.
        """
        rendered_html = DocumentHTML.transform(self.version, self.request)

        with self.layer.open_fixture(expected_filename) as expected:
            self.assertXMLEqual(expected.read(), rendered_html)

    def test_link_anchor(self):
        """Render a simple link with only an anchor.
        """
        self.set_document_xml('test_xslt_link.silvaxml')
        self.assertRenderingEqual('test_xslt_link.html')

    def test_link_tel(self):
        """Render a link with tel: schemata.
        """
        self.set_document_xml('test_xslt_link_tel.silvaxml')
        self.assertRenderingEqual('test_xslt_link_tel.html')


class CodeSourceXSLTRenderingTestCase(XSLTRenderingTestCase):
    """Test rendering of code-sources
    """

    def setUp(self):
        super(CodeSourceXSLTRenderingTestCase, self).setUp()
        self.version.content.manage_edit("""
<doc>
<p type="normal">Source result:</p>
<source id="codesource"></source>
</doc>
""")
        self.layer.login('manager')
        factory = self.root.manage_addProduct['SilvaExternalSources']
        factory.manage_addCodeSource('codesource', 'A Test Source', 'script')
        factory = self.root.codesource.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        self.layer.login('author')

    def set_source_script(self, script_data, parameters=None):
        """Set content of code source script used by the document.
        """
        self.layer.login('manager')
        if parameters is None:
            parameters = '##parameters=model,version,REQUEST'
        script = self.root.codesource.script
        script.write('\n'.join((parameters, '', script_data, '')))
        self.layer.login('author')

    def test_working_source(self):
        """Test a working code source rendering.
        """
        self.set_source_script(
            "return u'<p>I am a working source "
            "for %s.</p>' % version.get_title_or_id()")
        self.assertRenderingEqual('test_xslt_source.html')

    def test_broken_source(self):
        """Test a broken source that doesn't render because of errors.
        """
        self.set_source_script("return noexistant_var")
        self.assertRenderingEqual('test_xslt_source_broken.html')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XSLTRenderingTestCase))
    suite.addTest(unittest.makeSuite(CodeSourceXSLTRenderingTestCase))
    return suite

