# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_upgrade.py,v 1.1.8.3.4.1 2004/04/29 16:57:02 roman Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from xml.dom.minidom import parseString

from Testing import ZopeTestCase

import unittest

from Products.SilvaDocument import upgrade


class Rec:
    pass

class UpgradeTest(unittest.TestCase):

    def setUp(self):
        self.obj = Rec()

    def _xml_string(self,content):
        # dom to string; also ger rid of the first line, containing the '<?xml version=...?>
        return '\n'.join(content.toxml().split('\n')[1:])

    def test_xmlupgrade(self):
        dom = parseString('<p>foo<index name="bar">baz</index>bladibla</p>')
        self.obj.content = dom
        u = upgrade.UpgradeDocumentXML()
        u.upgrade(self.obj)
        xml = self._xml_string(self.obj.content)
        self.assertEquals('<p>foo<index name="bar"/>bazbladibla</p>', xml)

        dom = parseString('<p>foo<index name="bar">baz</index>bladibla<em><strong><index name="baz">bar</index></strong></em></p>')
        self.obj.content = dom
        u = upgrade.UpgradeDocumentXML()
        u.upgrade(self.obj)
        xml = self._xml_string(self.obj.content)
        self.assertEquals('<p>foo<index name="bar"/>bazbladibla<em><strong><index name="baz"/>bar</strong></em></p>', xml)

        dom = parseString('<table><row><field><index name="foo">foo</index></field></row><row><field><p><em><index name="bar">bar</index></em></p></field></row></table>')
        self.obj.content = dom
        u = upgrade.UpgradeDocumentXML()
        u.upgrade(self.obj)
        xml = self._xml_string(self.obj.content)
        self.assertEquals('<table><row><field><index name="foo"/>foo</field></row><row><field><p><em><index name="bar"/>bar</em></p></field></row></table>', xml)

    def test_xmlupgrade2(self):
        # XXX copy & paste tests ... could be done more elegant
        dom = parseString('<doc><p><em>foo</em></p><p><index name="bar">baz</index>bla</p></doc>')
        self.obj.content = dom
        u = upgrade.UpgradeDocumentXML()
        u.upgrade(self.obj)
        xml = self._xml_string(self.obj.content)
        self.assertEquals('<doc><p><em>foo</em></p><p><index name="bar"/>bazbla</p></doc>', xml)

    def test_xmlupgrade_table(self):
        # XXX copy & paste tests ... could be done more elegant
        # anyway, this test better does not fail, or the error message is pretty unreadable
        dom = parseString('<doc><p type="lead"><strong>a paragraph <index name="index_1">containing an index</index></strong></p><table columns="3"><row><field><p><strong>also <index name="index2">index</index> here</strong></p></field><field><p>and <index name="index3">index</index> here</p></field><field><p/><p type="normal">and <index name="index4"><strong>here</strong></index></p></field></row></table></doc>')

        self.obj.content = dom
        u = upgrade.UpgradeDocumentXML()
        u.upgrade(self.obj)
        xml = self._xml_string(self.obj.content)
        self.assertEquals('<doc><p type="lead"><strong>a paragraph <index name="index_1"/>containing an index</strong></p><table columns="3"><row><field><p><strong>also <index name="index2"/>index here</strong></p></field><field><p>and <index name="index3"/>index here</p></field><field><p/><p type="normal">and <index name="index4"/><strong>here</strong></p></field></row></table></doc>', xml)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UpgradeTest))
    return suite

def main():
    unittest.TextTestRunner(verbosity=2).run(test_suite())

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    main()
    
