# Copyright (c) 2008 Infrae. All rights reserverd.
# See also LICENSE.txt
# SilvaDocument
# Python

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

        ms_doc2 = """<html>
        <head><title></title>
        <link href="http://localhost:8087/silva_tranformer_test/frontend.css" type="text/css" rel="stylesheet" />
        <link href="http://localhost:8087/silva_tranformer_test/globals/kupu.css" type="text/css" rel="stylesheet" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="docref" content="x%DA%D3%60f%60%60%28%01b%86bQ%10%91%99S%96%18_R%94%98%97%96_%94%9BZ%14_%92Z%5CR%CC%01RS%9C%98%92%93%9D%96%05%00%1A%D7%0D%D3" />
        </head>
        <body>
        <h2></h2>


        <p>
        <span lang="EN-US">Dit <span>is</span>
        <strong>een</strong>
        </span>
        </p>
        </body>
        </html>"""
        src = str(transformer.to_source(ms_doc2, context=context))
        print src

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TransformerTest))
    return suite
