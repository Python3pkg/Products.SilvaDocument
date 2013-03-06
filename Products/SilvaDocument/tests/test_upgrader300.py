# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility

from Products.ParsedXML.ParsedXML import ParsedXML
from Products.SilvaDocument.testing import Functional30Layer
from Products.SilvaDocument.upgrader.upgrade_300 import document_upgrader
from Products.Silva.testing import TestCase

from silva.app.document.interfaces import IDocument, IDocumentVersion
from silva.core.interfaces import IOrderManager
from silva.core.layout.interfaces import IMarkManager
from silva.core.references.interfaces import IReferenceService
from silva.core.views.interfaces import IDisableBreadcrumbTag


class UpgraderTestCase(TestCase):
    layer = Functional30Layer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Information')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_upgrade_empty(self):
        """Upgrade a simple empty document.
        """
        document = self.root.document
        self.assertFalse(IDocument.providedBy(document))
        self.assertNotEqual(document.get_editable(), None)
        self.assertFalse(IDocumentVersion.providedBy(document.get_editable()))
        self.assertEqual(document.get_editable().get_title(), 'Information')
        self.assertEqual(document.get_viewable(), None)
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertNotEqual(upgraded.get_editable(), None)
        self.assertTrue(IDocumentVersion.providedBy(upgraded.get_editable()))
        self.assertEqual(document.get_editable().get_title(), 'Information')
        self.assertEqual(upgraded.get_viewable(), None)
        self.assertEqual(document_upgrader.validate(upgraded), False)

    def test_upgrade_simple_html(self):
        """Upgrade a document that contains some text.
        """
        document = self.root.document
        document.get_editable().content = ParsedXML(
            'document',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
   <p type="normal">This is a simple piece of text with two paragraph.</p>
   <p type="lead">This is the second paragraph.</p>
</doc>
""")

        # Upgrade the document
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertNotEqual(upgraded.get_editable(), None)
        version = upgraded.get_editable()
        self.assertEqual(version.get_title(), 'Information')
        self.assertXMLEqual(
            str(version.body),
            """
   <p>This is a simple piece of text with two paragraph.</p>
   <p class="lead">This is the second paragraph.</p>
""")

    def test_upgrade_unicode_html(self):
        """Upgrade a document that contains some text.
        """
        document = self.root.document
        document.get_editable().content = ParsedXML(
            'document',
            u"""<?xml version="1.0" encoding="utf-8"?>
<doc>
   <heading type="normal">Histoire d'un élève suisse</heading>
   <p type="normal">Il était une fois, un élève qui était allé à l'école étudier.</p>
   <p type="normal">Étant content, il étudiat.</p>
</doc>
""".encode('utf-8'))

        # Upgrade the document
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertNotEqual(upgraded.get_editable(), None)
        version = upgraded.get_editable()
        self.assertEqual(version.get_title(), 'Information')
        self.assertXMLEqual(
            str(version.body),
            """
   <h2>Histoire d'un &#233;l&#232;ve suisse</h2>
   <p>Il &#233;tait une fois, un &#233;l&#232;ve qui &#233;tait all&#233; &#224; l'&#233;cole &#233;tudier.</p>
   <p>&#201;tant content, il &#233;tudiat.</p>
""")

    def test_upgrade_html_with_image_reference(self):
        """Try to upgrade an image with a reference inside an HTML
        piece.
        """
        document = self.root.document
        version = document.get_editable()
        version.content = ParsedXML(
            'document',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
   <image alignment="align-center" reference="chocobo-master" />
</doc>
""")
        # Create the refered image
        factory = self.root.manage_addProduct['Silva']
        with self.layer.open_fixture('chocobo.jpg') as image:
            factory.manage_addImage('chocobo', 'Chocobo', image)
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"document image")
        reference.set_target(self.root.chocobo)
        reference.add_tag(u"chocobo-master")

        # Upgrade the document
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertNotEqual(upgraded.get_editable(), None)
        version = upgraded.get_editable()
        self.assertEqual(version.get_title(), 'Information')
        self.assertXMLEqual(
            str(version.body),
            """
<div class="image align-center">
 <img alt="Chocobo" reference="chocobo-master" />
</div>
""")


    def test_upgrade_html_with_image_path(self):
        """Try to upgrade an image with an URL inside an HTML piece.
        """
        document = self.root.document
        version = document.get_editable()
        version.content = ParsedXML(
            'document',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
   <image alignment="float-left" path="http://infrae.com/image.gif" />
</doc>
""")

        # Upgrade the document
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertNotEqual(upgraded.get_editable(), None)
        version = upgraded.get_editable()
        self.assertEqual(version.get_title(), 'Information')
        self.assertXMLEqual(
            str(version.body),
            """
<div class="image float-left">
 <img alt="" src="http://infrae.com/image.gif" />
</div>
""")

    def test_upgrade_html_with_link_reference(self):
        """Try to upgrade a link inside an HTML piece.
        """
        document = self.root.document
        version = document.get_editable()
        version.content = ParsedXML(
            'document',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
   <p>
     This is a link with a Silva reference to the
     <link target="_blank" reference="infrae-site" title="">Infrae site</link>.
   </p>
</doc>
""")
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addLink(
            'link', 'Link to Infrae', relative=False, url='http://infrae.com')
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"document link")
        reference.set_target(self.root.folder.link)
        reference.add_tag(u"infrae-site")

        # Upgrade the document
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertNotEqual(upgraded.get_editable(), None)
        version = upgraded.get_editable()
        self.assertEqual(version.get_title(), 'Information')
        self.assertXMLEqual(
            str(version.body),
            """
<p>
  This is a link with a Silva reference to the
  <a class="link" title="" target="_blank" reference="infrae-site">
    Infrae site
  </a>.
</p>
""")
        reference = service.get_reference(version, 'infrae-site')
        self.assertIsNot(reference.target, None)
        self.assertEqual(reference.target, self.root.folder.link)
        self.assertItemsEqual(
            list(service.get_references_from(version)), [reference])

    def test_upgrade_customization_markers(self):
        """Upgrade a document with a marker.
        """
        document = self.root.document
        IMarkManager(document).add_marker(IDisableBreadcrumbTag)
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertIn(IDisableBreadcrumbTag, IMarkManager(upgraded).usedMarkers)

    def test_upgrade_container_order(self):
        """Upgrade a document keep its position.
        """
        document = self.root.document
        order = IOrderManager(self.root)
        self.assertEqual(order.get_position(document), 0)
        self.assertEqual(order.get_position(self.root.folder), 1)
        self.assertEqual(document_upgrader.validate(document), True)
        self.assertNotEqual(document_upgrader.upgrade(document), document)

        upgraded = self.root.document
        order = IOrderManager(self.root)
        self.assertTrue(IDocument.providedBy(upgraded))
        self.assertEqual(order.get_position(upgraded), 0)
        self.assertEqual(order.get_position(self.root.folder), 1)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UpgraderTestCase))
    return suite

