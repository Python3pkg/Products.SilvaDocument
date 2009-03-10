# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_mixedcontentsupport.py,v 1.5 2006/01/24 16:15:05 faassen Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

import unittest
    
from Products.Silva.tests import SilvaTestCase

from Products.SilvaDocument import mixedcontentsupport
from Products.SilvaDocument import EditorSupportNested

class MixedContentSupport(SilvaTestCase.SilvaTestCase):
    
    def afterSetUp(self):
        self.mcr = mixedcontentsupport.SupportRegistry(
            mixedcontentsupport.ParagraphSupport)
    
    def test_defaultMixedContentSupport(self):
        metatype = 'foo'
        nodename = 'bar'
        supp = self.mcr.lookupByName(metatype, nodename)
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)

    def test_defaultMixedContentSupportLookup(self):
        doc = self.add_document(self.root, 'doc', u'Test Document')
        dom = doc.get_editable().content
        p = dom.createElement('p')        
        dom.documentElement.appendChild(p)
        h = dom.createElement('heading')        
        dom.documentElement.appendChild(h)
        pre = dom.createElement('pre')        
        dom.documentElement.appendChild(pre)
        document = dom.documentElement
        pelement = document.childNodes[0]
        supp = self.mcr.lookup(doc, pelement)
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        helement = document.childNodes[1]
        supp = self.mcr.lookup(doc, helement)
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        preelement = document.childNodes[2]
        supp = self.mcr.lookup(doc, preelement)
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        
    def test_registerDefaultForMetatype(self):
        metatype = 'foo'
        nodename = 'bar'
        self.mcr.registerMetaTypeDefault(
            metatype, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName(metatype, nodename)
        self.assertEquals(supp, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName(metatype, 'baz')
        self.assertEquals(supp, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName('waku', nodename)
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        supp = self.mcr.lookupByName('waku', 'baz')
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)

    def test_registerDefaultForNodeType(self):
        metatype = 'foo'
        nodename = 'bar'
        self.mcr.registerElementDefault(
            nodename, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName(metatype, nodename)
        self.assertEquals(supp, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName(metatype, 'baz')
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        supp = self.mcr.lookupByName('waku', nodename)
        self.assertEquals(supp, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName('waku', 'baz')
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        
    def test_register(self):
        metatype = 'foo'
        nodename = 'bar'
        self.mcr.register(
            metatype, nodename, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName(metatype, nodename)
        self.assertEquals(supp, mixedcontentsupport.PreSupport)
        supp = self.mcr.lookupByName(metatype, 'baz')
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        supp = self.mcr.lookupByName('waku', nodename)
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)
        supp = self.mcr.lookupByName('waku', 'baz')
        self.assertEquals(supp, mixedcontentsupport.ParagraphSupport)

class ParagraphSupport(SilvaTestCase.SilvaTestCase):

    def test_linkHelper(self):
        # Make a url that is known to cause a faulty return path:
        # 'http://nohost/root/http:localhost:8080/something'
        url1 = 'http://localhost:8080/something'
        # Get the ParagraphSupport object. Pass it an arbitrary html
        # snippet to satisfy the MixedContent object.
        p_support = mixedcontentsupport.ParagraphSupport('<p></p>')
        path1 = p_support._linkHelper(self.root, url1)
        self.assertEquals(path1, url1)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MixedContentSupport))
    suite.addTest(unittest.makeSuite(ParagraphSupport))
    return suite

def main():
    unittest.TextTestRunner(verbosity=2).run(test_suite())

if __name__ == '__main__':
    framework()
    
