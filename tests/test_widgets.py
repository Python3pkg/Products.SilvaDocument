# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_widgets.py,v 1.2.22.1 2004/04/29 16:57:02 roman Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

import unittest

from DateTime import DateTime
from Products.Silva.tests import SilvaTestCase
from Products.SilvaDocument.Document import Document

class DocumentEditTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.doc = self.add_document(self.root, 'doc', u'Test Document')
        self.doc_url = self.doc.absolute_url(1)
        self.root.REQUEST.SESSION={}

    def test_edit(self):
        request = self.root.REQUEST
        edit_xml = self.doc.get_editable().content
        doc_xml = edit_xml.documentElement

        # create an editor session by visiting tab_edit
        self.doc.edit['tab_edit']()

        self.assert_('no editor session created ?',
                     self.root.service_editor.hasNodeWidget(doc_xml))
        #print getitem(edit_xml,'widget,e0').edit.absolute_url(1)

        # its looks a but inconvenient to call the scripts via
        # item access, but soon one gets used to it ;-)

        # insert a new pragraph
        edit_xml['widget,e0'].edit['insert_mode']()
        edit_xml['widget,e0'].edit['insert'](what='p')

        self.assertEquals(1, len(doc_xml.childNodes) )
        self.assertEquals(u'p', doc_xml.childNodes[0].nodeName)
        new_paragraph = doc_xml.childNodes[0]
        p1_path = new_paragraph.getNodePath('widget')
        # new paragraph conains an empty text node
        self.assertEquals(1,len(new_paragraph.childNodes))
        self.assertEquals(new_paragraph.TEXT_NODE,
                          new_paragraph.firstChild.nodeType)
        self.assert_(not new_paragraph.firstChild.data)

        # add a few text to the paragraph
        request.form['what']='p'
        request.form['data']='some text'
        request.form['element_type']='normal'
        edit_xml[p1_path].edit['save']()
        self.assertEquals(u'some text',new_paragraph.firstChild.data)
        # we could test a lot more, but this is enough
        # to know how to write the next test


    def test_edit_published_document(self):
        # test that editing an already published document does not work
        # XXX: should also test that insert, move, etc .. does not work either
        # but thats a little much to type
        request = self.root.REQUEST
        edit_xml = self.doc.get_editable().content
        doc_xml = edit_xml.documentElement

        # create an editor session by visiting tab_edit
        self.doc.edit['tab_edit']()

        # insert a new pragraph
        #edit_xml['widget,e0'].edit['insert_mode']()
        edit_xml['widget,e0'].edit['insert'](what='p')
        new_paragraph = doc_xml.childNodes[0]
        p1_path = new_paragraph.getNodePath('widget')

        # now we publish the document:
        self.doc.set_unapproved_version_publication_datetime(DateTime() + 1)
        self.doc.approve_version()
        self.assertEquals(None, self.doc.get_editable())
        
        # try to add text to the paragraph: should fail, as already published
        request.form['what']='p'
        request.form['data']='some text'
        request.form['element_type']='normal'
        edit_xml[p1_path].edit['save']()
        self.assertEquals(u'',new_paragraph.firstChild.data)

        edit_xml[p1_path].edit['save_and_exit']()
        self.assertEquals(u'',new_paragraph.firstChild.data)

        edit_xml[p1_path].edit['save_and_insert']()
        self.assertEquals(u'',new_paragraph.firstChild.data)

        edit_xml[p1_path].edit['insert'](what='p')
        self.assertEquals(1, len(doc_xml.childNodes))

        edit_xml[p1_path].edit['delete']()
        self.assertEquals(1, len(doc_xml.childNodes))

        # we could test some more, but we would need more data
        # (e.g. to move up/down or edit a table ...)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentEditTestCase,'test'))
    return suite

def main():
    unittest.TextTestRunner(verbosity=2).run(test_suite())

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    main()
    
