# Copyright (c) 2002, 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_upgrade.py,v 1.1 2003/10/06 14:59:01 zagy Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from xml.dom.minidom import parseString

from Testing import ZopeTestCase

import unittest

from Products.SilvaDocument import upgrade

class UpgradeTest(unittest.TestCase):


    def test_xmlupgrade(self):
        class Rec:
            pass
        dom = parseString('<p>foo<index name="bar">baz</index>bladibla</p>')
        obj = Rec()
        obj.content = dom
        u = upgrade.UpgradeDocumentXML()
        u.upgrade(obj)
        xml = '\n'.join(obj.content.toxml().split('\n')[1:])
        self.assertEquals(xml, '<p>foobaz<index name="bar"/>bladibla</p>')
        
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
    
