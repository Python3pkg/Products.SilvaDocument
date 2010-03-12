# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.tests.SilvaTestCase import SilvaTestCase
from Products.SilvaDocument.transform import Transformer
from Products.SilvaDocument.transform.base import Context
from xml.parsers.expat import ExpatError


class KupuTransformerTest(SilvaTestCase):
    """Test HTML-Kupu transformer.
    """

    def afterSetUp(self):
        self.add_document(self.root, 'document', 'Document')
        self.transformer = Transformer.EditorTransformer(editor='kupu')
        # Context need the a document version in order to determine
        # references, and REQUEST to compute link URLs
        self.context = Context(self.root.document.1, self.REQUEST)

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

        node = self.transformer.to_source(targetobj=html, context=self.context)
        result = node.asBytes('utf-8')
        self.assertEqual(
            result,
            '<nlist type="disc"><li><p type="normal">foo</p>'
            '<list type="disc"><li>bar</li></list></li></nlist>')

        node = self.transformer.to_target(sourceobj=ret, context=self.context)
        roundtrip = node.asBytes('utf-8')

        self.assertEqual(roundtrip, html)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(KupuTransformerTest))
    return suite
