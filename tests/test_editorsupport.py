# Copyright (c) 2002, 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_editorsupport.py,v 1.2 2003/10/02 19:41:48 zagy Exp $

import Zope
Zope.startup()

import unittest

from Products.SilvaDocument.EditorSupportNested import Token, Scanner

class ScannerTest(unittest.TestCase):

    def test_simplebold(self):
        scanner = Scanner("++foobar++      blafasel")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 17)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].kind, Token.CHAR)
        self.assertEquals(t[1].text, 'f')
        self.assertEquals(t[6].text, 'r')
        self.assertEquals(t[7].kind, Token.EMPHASIS_END)
        self.assertEquals(t[8].kind, Token.WHITESPACE)
        self.assertEquals(t[9].text, 'b')
        
    def test_boldasterix(self):
        scanner = Scanner("*****")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 3)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].text, '*')
        self.assertEquals(t[2].kind, Token.STRONG_END)
       
    def test_boldasterix2(self):
        scanner = Scanner("******")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 4)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].text, '*')
        self.assertEquals(t[2].text, '*')
        self.assertEquals(t[3].kind, Token.STRONG_END)
      
    def test_italicplus(self):
        scanner = Scanner("+++++")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 3)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].text, '+')
        self.assertEquals(t[2].kind, Token.EMPHASIS_END)

    def test_bolditalic(self):
        scanner = Scanner("**++foobar++**")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 10)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].kind, Token.EMPHASIS_START)
        self.assertEquals(t[8].kind, Token.EMPHASIS_END)
        self.assertEquals(t[9].kind, Token.STRONG_END)
       
    def test_italicbold(self):
        scanner = Scanner("++**foobar**++")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 10)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].kind, Token.STRONG_START)
        self.assertEquals(t[8].kind, Token.STRONG_END)
        self.assertEquals(t[9].kind, Token.EMPHASIS_END)
       
    def test_underline(self):
        scanner = Scanner("__i am underlined__")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 17)
        self.assertEquals(t[0].kind, Token.UNDERLINE_START)
        self.assertEquals(t[16].kind, Token.UNDERLINE_END)
         
    def test_underline2(self):
        scanner = Scanner("__under**lined and **bold** and st__uff__")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 37)
        self.assertEquals(t[0].kind, Token.UNDERLINE_START)
        self.assertEquals(t[6].text, '*')
        self.assertEquals(t[18].kind, Token.STRONG_START)
        self.assertEquals(t[23].kind, Token.STRONG_END)
        self.assertEquals(t[36].kind, Token.UNDERLINE_END)
      

    def test_inlintestart(self):
        texts = [
            "This is __ just text",
            "This is (**) also just text",
            "This alike: [**]",
            ]
        for text in texts:
            scanner = Scanner(text)
            scanner.scan()
            t = scanner.tokens
            self.assertEquals(len(t), len(text))

    def test_url(self):
        urls = [
            'http://www.asdf.com',
            'mailto:foo@bar.com',
            'foo@bar.com',
            'ftp://bla.fasel/',
            'https://asdf.com/blablubb/sdfa/df/dfa?sdfasd=434&ds=ddf%20#foo'
        ]
        for url in urls:
            scanner = Scanner(url)
            scanner.scan()
            t = scanner.tokens
            self.assertEquals(len(t), 1)
            t = t[0]
            self.assertEquals(t.kind, t.LINK_URL)
            self.assertEquals(t.text, url)

    def test_link(self):
        scanner = Scanner("click ((here|http://here.com)) to see")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 21)
        self.assertEquals(t[6].kind, Token.LINK_START)
        self.assertEquals(t[7].text, 'h')
        self.assertEquals(t[11].kind, Token.LINK_SEP)
        self.assertEquals(t[12].kind, Token.LINK_URL)
        self.assertEquals(t[13].kind, Token.LINK_END)

    def test_linktarget(self):
        scanner = Scanner("click ((here|http://here.com|_top)) to see")
        scanner.scan()
        t = scanner.tokens
        self.assertEquals(len(t), 26)
        self.assertEquals(t[6].kind, Token.LINK_START)
        self.assertEquals(t[7].text, 'h')
        self.assertEquals(t[11].kind, Token.LINK_SEP)
        self.assertEquals(t[12].kind, Token.LINK_URL)
        self.assertEquals(t[13].kind, Token.LINK_SEP)
        self.assertEquals(t[14].text, '_')
        self.assertEquals(t[18].kind, Token.LINK_END)

    def test_supersubscript(self):
        scanner = Scanner("a~~1~~^^2^^+a~~2~~^^2^^=a~~3~~^^2^^")
        scanner.scan()
        t = scanner.tokens
        print t
        self.assertEquals(len(t), 27)
        self.assertEquals(t[0].text, 'a')
        self.assertEquals(t[1].kind, Token.SUBSCRIPT_START)
        self.assertEquals(t[3].kind, Token.SUBSCRIPT_END)
        self.assertEquals(t[4].kind, Token.SUPERSCRIPT_START)
        self.assertEquals(t[6].kind, Token.SUPERSCRIPT_END)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ScannerTest))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
