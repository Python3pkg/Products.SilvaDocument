# Copyright (c) 2008 Infrae. All rights reserverd.
# See also LICENSE.txt
# SilvaDocument
# Python

import unittest
from Products.Silva.tests.SilvaTestCase import SilvaTestCase
from Products.SilvaDocument.transform import Transformer
from xml.parsers.expat import ExpatError

class TransformerTest(SilvaTestCase):

    def test_to_source(self):
        #import pdb; pdb.set_trace()
        transformer = Transformer.EditorTransformer()
        src = str(transformer.to_source('<p>Hi</p>'))
        self.assertEqual(src, '[\'<p type="normal">Hi</p>\']')
        # None html bad text
        self.assertRaises(ExpatError, transformer.to_source, 'Hi')
        # Not well-formed
        self.assertRaises(ExpatError, transformer.to_source,
                          '<p>Hi<</p><br/>')
        # Mismatched tags
        self.assertRaises(ExpatError, transformer.to_source,
                          '<p>Hi<br></p>')
        # Pass a header in a list
        src = str(transformer.to_source('<ul><li><h3>Foo</h3></li></ul>'))
        ret = '[\'<nlist type="disc"><li><heading type="normal">Foo</heading></li></nlist>\']'
        self.assertEqual(src, ret)
        # Pass copied MS word doc text
        ms = """<p class="MsoNormal" style="margin-left: 35.4pt; text-indent: -35.4pt;"><span style="" lang="EN-US">Dit <span style="color: red;">is</span>
<b style="">een</b> </span><i style=""><span style="font-size: 24pt;" lang="EN-US">test</span></i><span style="" lang="EN-US"><o:p></o:p></span></p>"""
        self.assertRaises(ExpatError, transformer.to_source, ms)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TransformerTest))
    return suite
