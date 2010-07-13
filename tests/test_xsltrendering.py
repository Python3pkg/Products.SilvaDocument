# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.publisher.browser import TestRequest

from Products.Silva.tests.helpers import open_test_file
from Products.Silva.testing import FunctionalLayer, TestCase
from Products.SilvaDocument.Document import DocumentHTML


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

    def assertRenderingEqual(self, source_filename, expected_filename):
        with open_test_file(source_filename, globals()) as source:
            self.version.content.manage_edit(source.read())

        rendered_html = DocumentHTML.transform(self.version, self.request)

        with open_test_file(expected_filename, globals()) as expected:
            self.assertXMLEqual(expected.read(), rendered_html)

    def test_link_anchor(self):
        self.assertRenderingEqual(
            'test_xslt_link.silvaxml', 'test_xslt_link.html')

    def test_link_tel(self):
        self.assertRenderingEqual(
            'test_xslt_link_tel.silvaxml', 'test_xslt_link_tel.html')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XSLTRenderingTestCase))
    return suite

