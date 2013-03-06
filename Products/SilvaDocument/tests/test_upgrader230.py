# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.SilvaDocument.testing import FunctionalLayer
from Products.ParsedXML.ParsedXML import ParsedXML

from silva.core.references.interfaces import IReferenceService
from Products.SilvaDocument.upgrader.upgrade_230 import document_upgrader
from Products.SilvaDocument.upgrader.utils import split_path
from zope import component


class DocumentUpgraderTestCase(unittest.TestCase):
    """Test upgrader which rewrites links and images to use
    references.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')
        with self.layer.open_fixture('chocobo.jpg') as image:
            factory.manage_addImage('chocobo', 'Chocobo', image)
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')

    def test_split_path(self):
        """Test split path utility.
        """
        zope_root = self.root.getPhysicalRoot()
        self.assertEqual(
            split_path('publication/document', self.root),
            (['root', 'publication', 'document'], zope_root))
        self.assertEqual(
            split_path('/publication/document', self.root),
            (['publication', 'document'], zope_root))
        self.assertEqual(
            split_path('./../root/publication/document', self.root),
            (['root', 'publication', 'document'], zope_root))
        self.assertEqual(
            split_path('./document', self.root.publication),
            (['root', 'publication', 'document'], zope_root))
        self.assertEqual(
            split_path('.//document', self.root.publication, self.root),
            (['publication', 'document'], self.root))
        self.assertEqual(
            split_path('./.././publication/document',
                       self.root.publication, self.root),
            (['publication', 'document'], self.root))

    def test_upgrade_link(self):
        """Test upgrade of a simple link.
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="./publication">Publication link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('url'))
        self.assertFalse(link.hasAttribute('anchor'))
        reference_name = link.getAttribute('reference')
        reference_service = component.getUtility(IReferenceService)
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.publication)

    def test_upgrade_link_spaces(self):
        """Test upgrade of a simple link with spaces in the path.
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url=" ./publication">Publication link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('url'))
        self.assertFalse(link.hasAttribute('anchor'))
        reference_name = link.getAttribute('reference')
        reference_service = component.getUtility(IReferenceService)
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.publication)

    def test_upgrade_link_absolute_path(self):
        """Test upgrade of a simple link
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="/root/publication">Publication link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('url'))
        self.assertFalse(link.hasAttribute('anchor'))
        reference_name = link.getAttribute('reference')
        reference_service = component.getUtility(IReferenceService)
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.publication)

    def test_upgrade_link_absolute_path_from_silva(self):
        """Test upgrade of a simple link
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="/publication">Publication link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('url'))
        self.assertFalse(link.hasAttribute('anchor'))
        reference_name = link.getAttribute('reference')
        reference_service = component.getUtility(IReferenceService)
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.publication)

    def test_upgrade_link_not_silva_object(self):
        """Test upgrade of a link that does not point to a Silva
        object, like for instance to the edit interface.
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="./edit">SMI</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertTrue(link.hasAttribute('url'))
        self.assertEquals(link.getAttribute('url'), './edit')
        self.assertFalse(link.hasAttribute('anchor'))

    def test_upgrade_link_too_high(self):
        """Test upgrade of a link that have an invalid relative path
        to something not possible (like too many ..).
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="./../../../MANAGE">ME HACKER</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertTrue(link.hasAttribute('url'))
        self.assertEquals(link.getAttribute('url'), './../../../MANAGE')
        self.assertFalse(link.hasAttribute('anchor'))

    def test_upgrade_link_only_anchor(self):
        """Test upgrade of a link that is only to an anchor on the
        same page
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="#on_me">On me link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('url'))
        self.assertTrue(link.hasAttribute('anchor'))
        self.assertEqual(link.getAttribute('anchor'), 'on_me')

    def test_upgrade_link_only_anchor_spaces(self):
        """Test upgrade of a link that is only to an anchor on the
        same page
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url=" #on_me ">On me link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('url'))
        self.assertTrue(link.hasAttribute('anchor'))
        self.assertEqual(link.getAttribute('anchor'), 'on_me')

    def test_upgrade_link_with_anchor(self):
        """Test upgrade of a simple link to a content with an anchor
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="./publication#on_me">On me link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('url'))
        self.assertTrue(link.hasAttribute('anchor'))
        self.assertEqual(link.getAttribute('anchor'), 'on_me')
        reference_name = link.getAttribute('reference')
        reference_service = component.getUtility(IReferenceService)
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.publication)

    def test_upgrade_link_invalid(self):
        """Test upgrade of a simple link with a completely invalid
        URL as a link.
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content', u"""<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="Aléatoire">On me link</link>
  </p>
</doc>""".encode('utf-8'))
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('url'))
        self.assertEqual(link.getAttribute('url'), u'Aléatoire')
        self.assertFalse(link.hasAttribute('anchor'))
        self.assertFalse(link.hasAttribute('reference'))

    def test_upgrade_link_external(self):
        """Test upgrade of a link which is an external URL
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="http://infrae.com#top">Infrae link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('anchor'))
        self.assertTrue(link.hasAttribute('url'))
        url = link.getAttribute('url')
        self.assertEqual(url, 'http://infrae.com#top')

    def test_upgrade_link_external_spaces(self):
        """Test upgrade of a link which is an external URL
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url=" http://infrae.com#top ">Infrae link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertFalse(link.hasAttribute('anchor'))
        self.assertTrue(link.hasAttribute('url'))
        url = link.getAttribute('url')
        self.assertEqual(url, 'http://infrae.com#top')

    def test_upgrade_link_broken(self):
        """Test upgrade of a link which is an external URL
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <link target="_blank" url="./../publication/inexisting_document">Document link</link>
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertTrue(link.hasAttribute('url'))
        url = link.getAttribute('url')
        self.assertEqual(url, './../publication/inexisting_document')

    def test_upgrade_image(self):
        """Test upgrade of an image, regular without any link
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <image alignment="image-left" title="" width="600" image_title="Chocobo" rewritten_path="http://localhost/root/chocobo" target="_self" height="177" path="/root/chocobo" link_to_hires="0" link="" />
  </p>
</doc>""")
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement
        images = document_dom.getElementsByTagName('image')
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertTrue(image.hasAttribute('reference'))
        self.assertFalse(image.hasAttribute('path'))
        self.assertFalse(image.hasAttribute('rewritten_path'))
        self.assertFalse(image.hasAttribute('target'))
        self.assertFalse(image.hasAttribute('link'))
        self.assertFalse(image.hasAttribute('link_to_hires'))
        self.assertFalse(image.hasAttribute('silva_title'))
        self.assertTrue(image.hasAttribute('title'))
        self.assertEqual(image.getAttribute('title'), 'Chocobo')
        reference_name = image.getAttribute('reference')
        reference_service = component.getUtility(IReferenceService)
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.chocobo)

    def test_upgrade_image_link_to_hires(self):
        """Test to upgrade an image that contains a link to a hires
        version of itself.
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <image alignment="image-left" title="Big Chocobo" width="600" image_title="Chocobo" rewritten_path="http://localhost/root/chocobo" target="_self" height="177" path="chocobo" link_to_hires="1" link="" />
  </p>
</doc>""")
        reference_service = component.getUtility(IReferenceService)
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement

        # The converter added a link to the hires chocobo
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertTrue(link.hasAttribute('target'))
        self.assertEqual(link.getAttribute('target'), '_self')
        self.assertTrue(link.hasAttribute('title'))
        self.assertEqual(link.getAttribute('title'), 'Big Chocobo')
        reference_name = link.getAttribute('reference')
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.chocobo)

        # The image points to the chocobo as well
        images = link.childNodes
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertEqual(image.nodeName, 'image')
        self.assertTrue(image.hasAttribute('reference'))
        self.assertFalse(image.hasAttribute('path'))
        self.assertFalse(image.hasAttribute('rewritten_path'))
        self.assertFalse(image.hasAttribute('target'))
        self.assertFalse(image.hasAttribute('link'))
        self.assertFalse(image.hasAttribute('link_to_hires'))
        self.assertFalse(image.hasAttribute('silva_title'))
        self.assertTrue(image.hasAttribute('title'))
        self.assertEqual(image.getAttribute('title'), 'Chocobo')
        reference_name = image.getAttribute('reference')
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.chocobo)

        # There is only one image in the document
        images = document_dom.getElementsByTagName('image')
        self.assertEqual(len(images), 1)
        self.assertEqual(image, images[0])

    def test_upgrade_image_link(self):
        """Test to upgrade an image that contains a link to a
        different content in Silva.
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <image alignment="image-left" title="Pub" width="600" image_title="Chocobo" rewritten_path="http://localhost/root/chocobo" target="_blank" height="177" path="chocobo" link_to_hires="0" link="../publication" />
  </p>
</doc>""")
        reference_service = component.getUtility(IReferenceService)
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement

        # The converter added a link to the publication
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertTrue(link.hasAttribute('target'))
        self.assertEqual(link.getAttribute('target'), '_blank')
        self.assertTrue(link.hasAttribute('title'))
        self.assertEqual(link.getAttribute('title'), 'Pub')
        reference_name = link.getAttribute('reference')
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.publication)

        # The image points to the chocobo
        images = link.childNodes
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertEqual(image.nodeName, 'image')
        self.assertTrue(image.hasAttribute('reference'))
        self.assertFalse(image.hasAttribute('path'))
        self.assertFalse(image.hasAttribute('rewritten_path'))
        self.assertFalse(image.hasAttribute('target'))
        self.assertFalse(image.hasAttribute('link'))
        self.assertFalse(image.hasAttribute('link_to_hires'))
        self.assertFalse(image.hasAttribute('silva_title'))
        self.assertTrue(image.hasAttribute('title'))
        self.assertEqual(image.getAttribute('title'), 'Chocobo')
        reference_name = image.getAttribute('reference')
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.chocobo)

        # There is only one image in the document
        images = document_dom.getElementsByTagName('image')
        self.assertEqual(len(images), 1)
        self.assertEqual(image, images[0])

    def test_upgrade_image_broken_link(self):
        """Test to upgrade an missing image that contains a link to a
        different content in Silva.
        """
        document = self.root.document
        editable = self.root.document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <image alignment="image-left" title="Pub" width="600" image_title="Nothing" rewritten_path="http://localhost/root/nothing" target="_blank" height="177" path="nothing" link_to_hires="0" link="../publication" />
  </p>
</doc>""")
        reference_service = component.getUtility(IReferenceService)
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement

        # The converter added a link to the publication
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertTrue(link.hasAttribute('reference'))
        self.assertTrue(link.hasAttribute('target'))
        self.assertEqual(link.getAttribute('target'), '_blank')
        self.assertTrue(link.hasAttribute('title'))
        self.assertEqual(link.getAttribute('title'), 'Pub')
        reference_name = link.getAttribute('reference')
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.publication)

        # The image keeps its old path settings
        images = link.childNodes
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertEqual(image.nodeName, 'image')
        self.assertFalse(image.hasAttribute('reference'))
        self.assertTrue(image.hasAttribute('path'))
        self.assertEqual(image.getAttribute('path'), 'nothing')
        self.assertTrue(image.hasAttribute('rewritten_path'))
        self.assertEqual(
            image.getAttribute('rewritten_path'),
            'http://localhost/root/nothing')
        self.assertFalse(image.hasAttribute('target'))
        self.assertFalse(image.hasAttribute('link'))
        self.assertFalse(image.hasAttribute('link_to_hires'))
        self.assertFalse(image.hasAttribute('silva_title'))
        self.assertTrue(image.hasAttribute('title'))
        self.assertEqual(image.getAttribute('title'), 'Nothing')

        # There is only one image in the document
        images = document_dom.getElementsByTagName('image')
        self.assertEqual(len(images), 1)
        self.assertEqual(image, images[0])

    def test_upgrade_image_link_broken(self):
        """Test to upgrade an image that contains a link to a
        different missing content in Silva. This would be the same for
        link with external URLs.
        """
        document = self.root.document
        editable = document.get_editable()
        editable.content = ParsedXML(
            'content',
            """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p type="normal">
    <image alignment="image-left" title="Pub" width="600" image_title="Chocobo" rewritten_path="http://localhost/root/chocobo" target="_blank" height="177" path="chocobo" link_to_hires="0" link="foo_bar" />
  </p>
</doc>""")
        reference_service = component.getUtility(IReferenceService)
        self.assertEqual(document_upgrader.upgrade(document), document)
        document_dom = editable.content.documentElement

        # The converter added a link to the foo_bar URL.
        links = document_dom.getElementsByTagName('link')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertFalse(link.hasAttribute('reference'))
        self.assertTrue(link.hasAttribute('url'))
        self.assertEqual(link.getAttribute('url'), 'foo_bar')
        self.assertTrue(link.hasAttribute('target'))
        self.assertEqual(link.getAttribute('target'), '_blank')
        self.assertTrue(link.hasAttribute('title'))
        self.assertEqual(link.getAttribute('title'), 'Pub')

        # The image points to the chocobo
        images = link.childNodes
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertEqual(image.nodeName, 'image')
        self.assertTrue(image.hasAttribute('reference'))
        self.assertFalse(image.hasAttribute('path'))
        self.assertFalse(image.hasAttribute('rewritten_path'))
        self.assertFalse(image.hasAttribute('target'))
        self.assertFalse(image.hasAttribute('link'))
        self.assertFalse(image.hasAttribute('link_to_hires'))
        self.assertFalse(image.hasAttribute('silva_title'))
        self.assertTrue(image.hasAttribute('title'))
        self.assertEqual(image.getAttribute('title'), 'Chocobo')
        reference_name = image.getAttribute('reference')
        reference = reference_service.get_reference(
            editable, name=reference_name)
        self.assertEqual(reference.target, self.root.chocobo)

        # There is only one image in the document
        images = document_dom.getElementsByTagName('image')
        self.assertEqual(len(images), 1)
        self.assertEqual(image, images[0])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentUpgraderTestCase))
    return suite

