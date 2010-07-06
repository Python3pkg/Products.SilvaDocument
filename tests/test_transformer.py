# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from xml.parsers.expat import ExpatError

from Acquisition import aq_chain

from zope import component
from zope.intid.interfaces import IIntIds
from zope.publisher.browser import TestRequest

from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_id

from Products.Silva.testing import FunctionalLayer, TestCase
from Products.Silva.tests.helpers import publish_object, open_test_file
from Products.SilvaDocument.transform import Transformer
from Products.SilvaDocument.transform.base import Context

TEST_LINK_HTML = '<a silva_target="%d" href="reference" target="_blank" ' \
    'silva_reference="%s" title="">My link</a>'
TEST_IMAGE_HTML = '<img src="http://localhost/root/chocobo" ' \
    'silva_reference="%s" silva_target="%d" height="118" width="112" ' \
    'alt="Chocobo" alignment=""></img>'


class KupuTransformerTestCase(TestCase):
    """Test Silva<->Kupu transformer. Transformer are not anymore
    content-agnostic, because of reference management. Transforming
    Kupu->Silva do change the version it is transformed for.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')
        factory.manage_addImage(
            'chocobo', 'Chocobo', file=open_test_file('chocobo.jpg', globals()))
        self.transformer = Transformer.EditorTransformer(editor='kupu')
        # Context need the a document version in order to determine
        # references, and REQUEST to compute link URLs
        request = TestRequest()
        self.context = Context(self.root.document.get_editable(), request)

    def test_to_source(self):
        """Test conversion Kupu-format to Silva-format.
        """
        src = str(self.transformer.to_source('<p>Hi</p>', context=self.context))
        self.assertEqual(src, '[\'<p type="normal">Hi</p>\']')
        # None html bad text
        self.assertRaises(
            ExpatError,
            self.transformer.to_source,
            'Hi',
            context=self.context)

        # Not well-formed
        self.assertRaises(
            ExpatError,
            self.transformer.to_source,
            '<p>Hi<</p><br/>',
            context=self.context)

        # Mismatched tags
        self.assertRaises(
            ExpatError,
            self.transformer.to_source,
            '<p>Hi<br></p>',
            context=self.context)

        # Pass a header in a list
        src = str(self.transformer.to_source(
                '<ul><li><h3>Foo</h3></li></ul>',
                context=self.context))
        ret = '[\'<nlist type="disc"><li><heading type="normal">Foo</heading>' \
            '</li></nlist>\']'
        self.assertEqual(src, ret)

    def test_word_to_source(self):
        # Pass copied MS word doc text
        ms_doc1 = """<p class="MsoNormal" style="margin-left: 35.4pt; text-indent: -35.4pt;"><span style="" lang="EN-US">Dit <span style="color: red;">is</span>
<b style="">een</b> </span><i style=""><span style="font-size: 24pt;" lang="EN-US">test</span></i><span style="" lang="EN-US"><o:p></o:p></span></p>"""
        self.assertRaises(
            ExpatError,
            self.transformer.to_source,
            ms_doc1,
            context=self.context)

        ms_doc2 = """<p class="MsoNormal" style="margin-left: 35.4pt; text-indent: -35.4pt;"><span style="" lang="EN-US">Dit <span style="color: red;">is</span>
<b style="">een</b> </span><i style=""><span style="font-size: 24pt;" lang="EN-US">test</span></i><span style="" lang="EN-US"><o:p></o:p></span></p>


<h2 silva_id="new_test" silva_origin="silva_document"></h2>
<p class="normal">          &lt;p class="MsoNormal" style="margin-left: 35.4pt; text-indent: -35.4pt;"&gt;&lt;span style="" lang="EN-US"&gt;Dit &lt;span style="color: red;"&gt;is&lt;/span&gt;<br>&lt;b style=""&gt;een&lt;/b&gt; &lt;/span&gt;&lt;i style=""&gt;&lt;span style="font-size: 24pt;" lang="EN-US"&gt;test&lt;/span&gt;&lt;/i&gt;&lt;span style="" lang="EN-US"&gt;&lt;o:p&gt;&lt;/o:p&gt;&lt;/span&gt;&lt;/p&gt;</p>
<p class="normal"><br> Dit is <b>een</b> <i>test</i></p>"""
        self.assertRaises(
            ExpatError,
            self.transformer.to_source,
            ms_doc2,
            context=self.context)

    def test_nested_list_round_trip(self):
        # expected behaviour is that nested lists are always a child of a p
        # in silva, but are displayed as direct children in html because
        # contentEditable seems to like this structure more
        html = '<ul type="disc"><li><p class="normal">foo</p></li>' \
            '<ul type="disc"><li>bar</li></ul></ul>'

        result = self.transformer.to_source(
            targetobj=html, context=self.context).asBytes('utf-8')
        self.assertEqual(
            result,
            '<nlist type="disc"><li><p type="normal">foo</p>'
            '<list type="disc"><li>bar</li></list></li></nlist>')

        roundtrip = self.transformer.to_target(
            sourceobj=result, context=self.context).asBytes('utf-8')
        self.assertEqual(roundtrip, html)

    def test_new_image_round_trip(self):
        """We create a new image which is a reference to an image by
        transforming Kupu->Silva, and we check the result by
        transforming Silva->Kupu again.
        """
        service = component.getUtility(IReferenceService)
        target_id = component.getUtility(IIntIds).getId(self.root.chocobo)
        version = self.root.document.get_editable()

        # At first there is no references
        self.assertEqual(list(service.get_references_from(version)), [])
        self.assertEqual(list(service.get_references_to(self.root.chocobo)), [])

        html = TEST_IMAGE_HTML % ('new', target_id)

        # We convert our HTML with a new reference to Kupu
        node = self.transformer.to_source(targetobj=html, context=self.context)
        image = node.query_one('image')
        self.assertEqual(image.name(), 'image')
        self.failUnless(image.hasattr('title'))
        self.assertEqual(image.getattr('title'), 'Chocobo')
        self.failUnless(image.hasattr('reference'))
        reference_name = image.getattr('reference')
        result = node.asBytes('utf-8')
        self.assertEqual(
            result,
            '<image reference="%s" alignment="" title="Chocobo"></image>' % (
                reference_name))

        # We verify that the reference has been created.
        reference = service.get_reference(version, reference_name)
        self.failIf(reference is None)
        self.assertEqual(reference.source, version)
        self.assertEqual(reference.target, self.root.chocobo)
        self.assertEqual(reference.tags, [u"document link", reference_name])
        self.assertEqual(
            list(service.get_references_to(self.root.chocobo)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

        # We can get back the HTML with a reference name
        roundtrip = self.transformer.to_target(
            sourceobj=result, context=self.context).asBytes('utf-8')
        self.assertEqual(
            roundtrip,
            TEST_IMAGE_HTML % (reference_name, target_id))

        # Our new reference has been kept
        self.assertEqual(
            list(service.get_references_to(self.root.chocobo)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

    def test_new_link_round_trip(self):
        """We create a new link which is a reference to a content in
        Silva, by transforming Kupu->Silva, and verify we get back our
        link in Kupu by transforming Silva->Kupu.
        """
        service = component.getUtility(IReferenceService)
        target_id = component.getUtility(IIntIds).getId(self.root.folder)
        version = self.root.document.get_editable()

        # At first there is no references
        self.assertEqual(list(service.get_references_from(version)), [])
        self.assertEqual(list(service.get_references_to(self.root.folder)), [])

        html = TEST_LINK_HTML % (target_id, 'new')

        # We convert our HTML with a new reference to Kupu
        node = self.transformer.to_source(targetobj=html, context=self.context)
        link = node.query_one('link')
        self.assertEqual(link.name(), 'link')
        self.failUnless(link.hasattr('reference'))
        reference_name = link.getattr('reference')
        result = node.asBytes('utf-8')
        self.assertEqual(
            result,
            '<link target="_blank" reference="%s" title="">My link</link>' % (
                reference_name))

        # We verify that the reference has been created.
        reference = service.get_reference(version, reference_name)
        self.assertEqual(reference.source, version)
        self.assertEqual(aq_chain(reference.source), aq_chain(version))
        self.assertEqual(reference.target, self.root.folder)
        self.assertEqual(aq_chain(reference.target), aq_chain(self.root.folder))
        self.assertEqual(reference.tags, [u"document link", reference_name])
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

        # We can get back the HTML with a reference name
        roundtrip = self.transformer.to_target(
            sourceobj=result, context=self.context).asBytes('utf-8')
        self.assertEqual(
            roundtrip,
            TEST_LINK_HTML % (target_id, reference_name))

        # Our new reference has been kept
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

    def test_existing_link_round_trip(self):
        """We have an existing link in Kupu, that we keep by
        transforming Kupu->Silva, and see again in Kupu by
        transforming Silva->Kupu.
        """
        service = component.getUtility(IReferenceService)
        version = self.root.document.get_editable()
        reference = service.new_reference(version, name=u"document link")
        reference.set_target(self.root.folder)
        reference_name = u"existing-link-id"
        reference.add_tag(reference_name)

        # We have a reference
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

        html = TEST_LINK_HTML % (reference.target_id, reference_name)

        result = self.transformer.to_source(
            targetobj=html, context=self.context).asBytes('utf-8')
        self.assertEqual(
            result,
            '<link target="_blank" reference="%s" title="">My link</link>' % (
                reference_name))
        # We still only have one reference to the folder
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

        # We can get back the HTML we started from
        roundtrip = self.transformer.to_target(
            sourceobj=result, context=self.context).asBytes('utf-8')
        self.assertEqual(roundtrip, html)

        # Our new reference has been kept
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

    def test_existing_link_round_trip_on_copy(self):
        """We edit a existing link that have been created on a
        previous version of the document.
        """
        # Step one, create a link
        service = component.getUtility(IReferenceService)
        version = self.root.document.get_editable()
        reference = service.new_reference(version, name=u"document link")
        reference.set_target(self.root.folder)
        reference_name = u"existing-link-id"
        reference.add_tag(reference_name)

        # Step two, make a new copy
        publish_object(self.root.document)
        self.root.document.create_copy()
        new_version = self.root.document.get_editable()
        self.failIfEqual(version, new_version)
        new_reference = service.get_reference(new_version, name=reference_name)
        self.failIfEqual(reference, new_reference)

        # Now, the target is point by two relations, one for each version
        self.assertEqual(
            list(service.get_references_to(self.root.publication)),
            [])
        self.assertListEqual(
            list(service.get_references_to(self.root.folder)),
            [reference, new_reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(new_version)),
            [new_reference])

        # To spice up the situation, we are going to modify the
        # reference on the new version to the publication
        new_target_id = component.getUtility(IIntIds).getId(
            self.root.publication)

        html = TEST_LINK_HTML % (new_target_id, reference_name)

        context = Context(new_version, TestRequest())
        result = self.transformer.to_source(
            targetobj=html, context=context).asBytes('utf-8')
        self.assertEqual(
            result,
            '<link target="_blank" reference="%s" title="">My link</link>' % (
                reference_name))

        # Now, things are changed correctly
        self.assertEqual(
            list(service.get_references_to(self.root.publication)),
            [new_reference])
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(new_version)),
            [new_reference])

        # We can get back the HTML we started from for the new version
        roundtrip = self.transformer.to_target(
            sourceobj=result, context=context).asBytes('utf-8')
        self.assertEqual(roundtrip, html)

        # And things stays the same
        self.assertEqual(
            list(service.get_references_to(self.root.publication)),
            [new_reference])
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(new_version)),
            [new_reference])

    def test_delete_link_round_trip(self):
        """We have an existing link that we removed in Kupu, so when
        we transform Kupu->Silva it is removed from the version we
        edit as well.
        """
        service = component.getUtility(IReferenceService)
        version = self.root.document.get_editable()
        reference = service.new_reference(version, name=u"document link")
        reference.set_target(self.root.folder)
        reference_name = u"existing-link-id"
        reference.add_tag(reference_name)

        # We have a reference
        self.assertEqual(
            list(service.get_references_to(self.root.folder)),
            [reference])
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

        # Reference have been removed in favor of an anchor
        html = '<a title="Anchor" class="index" name="anchor">'\
            '[#anchor: Anchor]</a>'
        result = self.transformer.to_source(
            targetobj=html, context=self.context).asBytes('utf-8')

        # The reference should be gone
        self.assertEqual(list(service.get_references_from(version)), [])
        self.assertEqual(list(service.get_references_to(self.root.folder)), [])

        # (and we get back our anchor)
        roundtrip = self.transformer.to_target(
            sourceobj=result, context=self.context).asBytes('utf-8')
        self.assertEqual(roundtrip, html)

        # (and still no references)
        self.assertEqual(list(service.get_references_from(version)), [])
        self.assertEqual(list(service.get_references_to(self.root.folder)), [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(KupuTransformerTestCase))
    return suite
