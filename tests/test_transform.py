# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from StringIO import StringIO

from Products.SilvaDocument.transform.Transformer import EditorTransformer
from Products.SilvaDocument.transform.base import Context

class TransformTestCase(unittest.TestCase):
    def test_nested_list_round_trip(self):
        # expected behaviour is that nested lists are always a child of a p
        # in silva, but are displayed as direct children in html because
        # contentEditable seems to like this structure more
        html = ('<ul type="disc"><li><p class="normal">foo</p></li>'
                '<ul type="disc"><li>bar</li></ul></ul>')
        t = EditorTransformer(editor='kupu')
        ctx = Context(f=StringIO(html),
                      last_version=1,
                      url='http://foo.bar',
                      browser='Mozilla',
                      model=None)
        node = t.to_source(targetobj=html, context=ctx)
        ret = node.asBytes('utf-8')
        assert ret == ('<nlist type="disc"><li><p type="normal">foo</p>'
                       '<list type="disc"><li>bar</li></list></li></nlist>')
        node = t.to_target(sourceobj=ret, context=ctx)
        roundtrip = node.asBytes('utf-8')
        assert roundtrip == html

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TransformTestCase))
    return suite
