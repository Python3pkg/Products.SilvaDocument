# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_editorsupport.py,v 1.19 2005/01/19 14:28:51 faassen Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

import unittest
from xml.dom.minidom import parseString

from Products.SilvaDocument.EditorSupportNested import EditorSupport

class EditableTest(unittest.TestCase):

    def test_escape(self):
        
        cases = [
            ('foobar', 'foobar'),
            ('<em>foobar</em>', '<i>foobar</i>'),
            ('<strong>foobar</strong>', '<b>foobar</b>'),
            ('<strong>foo<em>bar</em></strong>', '<b>foo<i>bar</i></b>'),
            ('<link url="http://slashdot.org">slashdot</link>',
                '<a href="http://slashdot.org">slashdot</a>'),
            ('<link url="http://slashdot.org" target="foo">slashdot</link>',
                '<a href="http://slashdot.org" target="foo">slashdot</a>'),
            ('<link url="http://slashdot.org" target="_blank">slashdot</link>',
                '<a href="http://slashdot.org" target="_blank">slashdot</a>'),
        ]
        
        es = EditorSupport('')
        
        for xml_text, expected_editable in cases:
            dom = parseString('<p>%s</p>' % xml_text)
            # This tests the old style API in EditorSupport
            editable = es.render_text_as_editable(dom.firstChild)
            self.assertEquals(expected_editable, editable,
                '%s was converted to %s, instead of %s' % (xml_text,
                    editable, expected_editable))

    def test_pre(self):
        cases = [
            ('&amp;foobar;', '&foobar;'),
            ('&amp;&lt;&gt;&quot;', '&<>"'),
            ('foo  bar', 'foo  bar'),
        ]
        
        es = EditorSupport('')
        for xml_text, expected_editable in cases:
            dom = parseString('<pre>%s</pre>' % xml_text)
            # This tests the old style API in EditorSupport
            editable = es.render_pre_as_editable(dom.firstChild)
            self.assertEquals(expected_editable, editable,
                '%s was converted to %s, instead of %s' % (xml_text,
                    editable, expected_editable))
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EditableTest))
    return suite

if __name__ == '__main__':
    try:
        # if we have hotshot just profile everyting.
        from hotshot import Profile
        p = Profile('editorsupport.hotshot')
        p.runcall(framework)
    except ImportError:
        framework()
    
