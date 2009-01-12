# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.tests.SilvaTestCase import SilvaTestCase
from Products.SilvaDocument.transform import Transformer
from Products.SilvaDocument.transform.base import Context
from xml.parsers.expat import ExpatError

class TransformerTest(SilvaTestCase):

    def test_to_source(self):
        #import pdb; pdb.set_trace()
        transformer = Transformer.EditorTransformer()
        context = Context(browser='IE')
        src = str(transformer.to_source('<p>Hi</p>', context=context))
        self.assertEqual(src, '[\'<p type="normal">Hi</p>\']')
        # None html bad text
        self.assertRaises(ExpatError,
                          transformer.to_source,
                          'Hi',
                          context=context)
        # Not well-formed
        self.assertRaises(ExpatError,
                          transformer.to_source,
                          '<p>Hi<</p><br/>',
                          context=context)
        # Mismatched tags
        self.assertRaises(ExpatError,
                          transformer.to_source,
                          '<p>Hi<br></p>',
                          context=context)
        # Pass a header in a list
        src = str(transformer.to_source('<ul><li><h3>Foo</h3></li></ul>',
                                        context=context))
        ret = '[\'<nlist type="disc"><li><heading type="normal">Foo</heading></li></nlist>\']'
        self.assertEqual(src, ret)
        # Pass copied MS word doc text
        ms_doc1 = """<p class="MsoNormal" style="margin-left: 35.4pt; text-indent: -35.4pt;"><span style="" lang="EN-US">Dit <span style="color: red;">is</span>
<b style="">een</b> </span><i style=""><span style="font-size: 24pt;" lang="EN-US">test</span></i><span style="" lang="EN-US"><o:p></o:p></span></p>"""
        self.assertRaises(ExpatError,
                          transformer.to_source,
                          ms_doc1,
                          context=context)

        ms_doc2 = """<p class="MsoNormal" style="margin-left: 35.4pt; text-indent: -35.4pt;"><span style="" lang="EN-US">Dit <span style="color: red;">is</span>
<b style="">een</b> </span><i style=""><span style="font-size: 24pt;" lang="EN-US">test</span></i><span style="" lang="EN-US"><o:p></o:p></span></p>


<h2 silva_id="new_test" silva_origin="silva_document"></h2>
<p class="normal">          &lt;p class="MsoNormal" style="margin-left: 35.4pt; text-indent: -35.4pt;"&gt;&lt;span style="" lang="EN-US"&gt;Dit &lt;span style="color: red;"&gt;is&lt;/span&gt;<br>&lt;b style=""&gt;een&lt;/b&gt; &lt;/span&gt;&lt;i style=""&gt;&lt;span style="font-size: 24pt;" lang="EN-US"&gt;test&lt;/span&gt;&lt;/i&gt;&lt;span style="" lang="EN-US"&gt;&lt;o:p&gt;&lt;/o:p&gt;&lt;/span&gt;&lt;/p&gt;</p>
<p class="normal"><br> Dit is <b>een</b> <i>test</i></p>"""
        self.assertRaises(ExpatError,
                          transformer.to_source,
                          ms_doc2,
                          context=context)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TransformerTest))
    return suite
