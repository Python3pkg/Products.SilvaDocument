# Copyright (c) 2002, 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_editorsupport.py,v 1.4 2003/10/06 08:05:03 zagy Exp $

import Zope
Zope.startup()

import unittest
import time

from Products.SilvaDocument.EditorSupportNested import \
    Token, Parser, Interpreter

class ParserTest(unittest.TestCase):

    large_text = """Kaum standen am folgenden Tage die hohen Felsengipfel im Glanz des Sonnenlichts, so hüpfte Gustav aus dem Bette und fand - wem kommt dabey nicht das ehemahls selbst genossene kindische Entzücken beym Anblick des Weihnachtsgeschenks ins Gedächtniss? - einen netten Anzug auf dem Stuhle am Bette, den die Gattinn des Schultheissen von den Söhnen eines im Flecken wohnenden Edelmannes, einstweilen angenommen hatte, da sich nicht so schnell, als sie es jetzt wünschte, die Nähnadeln zu Buchenthal in Bewegung setzen liessen. Ewalds hatten ein Weilchen auf das Benehmen des kleinen Lieblings gelauscht, und öffneten das Gemach, als sich eben seine Empfindungen in ein lautes »Ach wie schön!« auflösten. »Guten Tag, Papa, guten Tag, Mama!« schluchzte Gustav, und eilte den Kommenden entgegen, um mit tausend Händeküssen ihnen Dank und Liebe zu zollen. Die guten Alten staunten bey dem seltenen Feingefühl eines so kleinen Knaben, und hätten von diesem Augenblicke gegen die Schätze von Golconda, dem aufgenommenen Pflegling nicht entsagt. Die muthigen Apfelschimmel stampften schon ungeduldig im Hofe den Boden. Gustav stack geschwind mit Ewalds Hülfe in dem ganz passenden Anzuge, und glich einem jungen Liebesgott, indess die Gattin des Schultheissen alle die kleinen häuslichen Angelegenheiten und die Geschäfte des Tages an das Gesinde austheilte, ihm nochmahls Achtsamkeit und Fleiss empfahl, genoss Gustav eine wohlschmeckende Milchsuppe, denn Caffee kam selten, bloss bey ganz ausnehmenden Fällen, in Ewalds Haus, weil diese Leute einen gewissen edlen Stolz im Entsagen allen dessen, was das Ausland zeugte, suchten, und sich genügsam an das, was auf heimathlichem Boden wuchs, hielten. Auch kannte Ewald lebende Beyspiele genug, dass Neigung und Geschmack an dem, das Blut in Wallung setzenden - und schlecht gekocht, den Magen schlaff machenden - Caffee sich beym weiblichen Geschlechte so leicht in Leidenschaft umwandle, als beym männlichen die Liebe zum Schnaps. Seine Familie zählte einige unglückliche Beweise dieses Satzes, die dem wohlwollenden Manne eine unumstössliche Abneigung gegen diese Schote einflössten, obschon seine ökonomische Lage ihm allenfalls auch heutigen Tages, wo Caffee so ungemein gestiegen ist, dass man ihn kaum bezahlen kann - gestattet hätte, denselben ohne deutsche Mengsel und sonstige Hülfsmittel, die Caffee heissen, ohne es zu seyn, zwey Mahl täglich zu geniessen. Dächten und handelten doch alle Deutsche wie Ewald! Zehnmahl hatte die geschäftige Alte alle nöthigen Befehle schon gegeben, und eben so oft noch eine Kleinigkeit nachzuholen. Jetzt suchte sie einen Schlüssel, den sie in den Händen hielt, dann einen Pelzmantel, den sie im Juny doch gewiss nicht nöthig hatte. Ewald lächelte und ging an den Wagen. Das gute Hausweib hatte, obschon es nahe an den Sechzigen stand, noch keinen vollen Tag die Pfähle im Stich gelassen, in denen es von Jugend auf lebte und webte; bloss Theilnahme und Liebe zu Gustav, konnte es zu diesem Entschluss bewegen. Endlich kam sie mit zwey Schachteln von ziemlichem Umfange voll Victualien, eine Magd folgte mit einem dito Sack, und hinten auf dem Wagen blöckten zwey festgebundene Hammel um baldige Entlassung aus so lässigen Fesseln. Die Hofhunde bellten zum Abschiede, Hans schwang die Peitsche, und pfeilschnell flogen die ungeduldigen Apfelschimmel zum Flecken hinaus. Glück auf den Weg!"""
    
    def test_simpleemph(self):
        parser = Parser("++foobar++      blafasel")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 5)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].kind, Token.CHAR)
        self.assertEquals(t[1].text, 'foobar')
        self.assertEquals(t[2].kind, Token.EMPHASIS_END)
        self.assertEquals(t[3].kind, Token.WHITESPACE)
        self.assertEquals(t[4].text, 'blafasel')
        
    def test_boldasterix(self):
        parser = Parser("*****")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 3)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].text, '*')
        self.assertEquals(t[2].kind, Token.STRONG_END)
       
    def test_boldasterix2(self):
        parser = Parser("******")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 4)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].text, '*')
        self.assertEquals(t[3].kind, Token.STRONG_END)
      
    def test_italicplus(self):
        parser = Parser("+++++")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 3)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].text, '+')
        self.assertEquals(t[2].kind, Token.EMPHASIS_END)

    def test_bolditalic(self):
        parser = Parser("**++foobar++**")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 5)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].kind, Token.EMPHASIS_START)
        self.assertEquals(t[3].kind, Token.EMPHASIS_END)
        self.assertEquals(t[4].kind, Token.STRONG_END)
       
    def test_italicbold(self):
        parser = Parser("++**foobar**++")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 5)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].kind, Token.STRONG_START)
        self.assertEquals(t[3].kind, Token.STRONG_END)
        self.assertEquals(t[4].kind, Token.EMPHASIS_END)
       
    def test_underline(self):
        parser = Parser("__i am underlined__")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 7)
        self.assertEquals(t[0].kind, Token.UNDERLINE_START)
        self.assertEquals(t[6].kind, Token.UNDERLINE_END)
         
    def test_underline2(self):
        parser = Parser("__under**lined and **bold** and st__uff__")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 19)
        self.assertEquals(t[0].kind, Token.UNDERLINE_START)
        self.assertEquals(t[3].text, '*')
        self.assertEquals(t[8].kind, Token.STRONG_START)
        self.assertEquals(t[10].kind, Token.STRONG_END)
        self.assertEquals(t[18].kind, Token.UNDERLINE_END)
      

    def test_inlintestart(self):
        texts = [
            ("This is __ just text", 10),
            ("This is (**) also just text", 14),
            ("This alike: [**]", 9),
            ]
        for text, length in texts:
            parser = Parser(text)
            parser.run()
            t = parser.getResult().tokens
            self.assertEquals(len(t), length)

    def test_url(self):
        urls = [
            'http://www.asdf.com',
            'mailto:foo@bar.com',
            'foo@bar.com',
            'ftp://bla.fasel/',
            'https://asdf.com/blablubb/sdfa/df/dfa?sdfasd=434&ds=ddf%20#foo'
        ]
        for url in urls:
            parser = Parser(url)
            parser.run()
            t = parser.getResult().tokens
            self.assertEquals(len(t), 1)
            t = t[0]
            self.assertEquals(t.kind, t.LINK_URL)
            self.assertEquals(t.text, url)

    def test_link(self):
        parser = Parser("click ((here|http://here.com)) to see")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 11)
        self.assertEquals(t[2].kind, Token.LINK_START)
        self.assertEquals(t[3].text, 'here')
        self.assertEquals(t[4].kind, Token.LINK_SEP)
        self.assertEquals(t[5].kind, Token.LINK_URL)
        self.assertEquals(t[6].kind, Token.LINK_END)

    def test_linktarget(self):
        parser = Parser("click ((here|http://here.com|_top)) to see")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 14)
        self.assertEquals(t[2].kind, Token.LINK_START)
        self.assertEquals(t[3].text, 'here')
        self.assertEquals(t[4].kind, Token.LINK_SEP)
        self.assertEquals(t[5].kind, Token.LINK_URL)
        self.assertEquals(t[6].kind, Token.LINK_SEP)
        self.assertEquals(t[7].text, '_')
        self.assertEquals(t[9].kind, Token.LINK_END)

    def test_superscriptbold(self):
        parser = Parser("**foo^^bar^^**")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 6)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].text, 'foo')
        self.assertEquals(t[2].kind, Token.SUPERSCRIPT_START)
        self.assertEquals(t[3].text, 'bar')
        self.assertEquals(t[4].kind, Token.SUPERSCRIPT_END)
        self.assertEquals(t[5].kind, Token.STRONG_END)
        
    
    def test_supersubscript(self):
        parser = Parser("a~~1~~^^2^^+a~~2~~^^2^^=a~~3~~^^2^^")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 23)
        self.assertEquals(t[0].text, 'a')
        self.assertEquals(t[1].kind, Token.SUBSCRIPT_START)
        self.assertEquals(t[3].kind, Token.SUBSCRIPT_END)
        self.assertEquals(t[4].kind, Token.SUPERSCRIPT_START)
        self.assertEquals(t[6].kind, Token.SUPERSCRIPT_END)

    def test_softbreak(self):
        parser = Parser("a\nb\n\n\n\nc")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 5)
        self.assertEquals(t[0].text, 'a')
        self.assertEquals(t[1].kind, Token.SOFTBREAK)
        self.assertEquals(t[2].text, 'b')
        self.assertEquals(t[3].kind, Token.SOFTBREAK)
        self.assertEquals(t[4].text, 'c')
       
    def test_largesimpletext(self):
        # this is basicly a speed test
        parser = Parser(self.large_text)
        parser.run()

    def test_index(self):
        parser = Parser("A Word[[Word]] blafasel")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 8)
        self.assertEquals(t[3].kind, Token.INDEX_START)
        self.assertEquals(t[5].kind, Token.INDEX_END)


    def test_escape(self):
        parser = Parser("In Silva markup **bold** is marked up as \**bold\**")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 23)
        self.assertEquals(t[21].kind, Token.ESCAPE)

class InterpreterTest(unittest.TestCase):

    t = Token
    helper_tests = [
        ([
            (t.STRONG_START, '**'),
            (t.CHAR, '*'),
            (t.STRONG_END, '**'),
        ], '<strong>*</strong>'),
        ([
            (t.EMPHASIS_START, '++'),
            (t.STRONG_START, '**'),
            (t.CHAR, 'f'),
            (t.CHAR, 'o'),
            (t.CHAR, 'o'),
            (t.CHAR, 'b'),
            (t.CHAR, 'a'),
            (t.CHAR, 'r'),
            (t.STRONG_END, '**'),
            (t.EMPHASIS_END, '++'),
            ], '<em><strong>foobar</strong></em>'),
        ([
            (t.UNDERLINE_START, '__'),
            (t.CHAR, 'u'),
            (t.CHAR, 'n'),
            (t.CHAR, 'd'),
            (t.CHAR, 'e'),
            (t.CHAR, 'r'),
            (t.CHAR, '*'),
            (t.CHAR, '*'),
            (t.CHAR, 'l'),
            (t.CHAR, 'i'),
            (t.CHAR, 'n'),
            (t.CHAR, 'e'),
            (t.CHAR, 'd'),
            (t.WHITESPACE, ' '),
            (t.CHAR, 'a'),
            (t.CHAR, 'n'),
            (t.CHAR, 'd'),
            (t.WHITESPACE, ' '),
            (t.STRONG_START, '**'),
            (t.CHAR, 'b'),
            (t.CHAR, 'o'),
            (t.CHAR, 'l'),
            (t.CHAR, 'd'),
            (t.STRONG_END, '**'),
            (t.WHITESPACE, ' '),
            (t.CHAR, 'a'),
            (t.CHAR, 'n'),
            (t.CHAR, 'd'),
            (t.WHITESPACE, ' '),
            (t.CHAR, 's'),
            (t.CHAR, 't'),
            (t.CHAR, '_'),
            (t.CHAR, '_'),
            (t.CHAR, 'u'),
            (t.CHAR, 'f'),
            (t.CHAR, 'f'),
            (t.UNDERLINE_END, '__'),
            ], '<underline>under**lined and <strong>bold</strong> and st__uff</underline>'),
        ([
            (t.CHAR, 'c'),
            (t.CHAR, 'l'),
            (t.CHAR, 'i'),
            (t.CHAR, 'c'),
            (t.CHAR, 'k'),
            (t.WHITESPACE, ' '),
            (t.LINK_START, '(('),
            (t.CHAR, 'h'),
            (t.CHAR, 'e'),
            (t.CHAR, 'r'),
            (t.CHAR, 'e'),
            (t.LINK_SEP, '|'),
            (t.LINK_URL, 'http://here.com'),
            (t.LINK_END, '))'),
            (t.WHITESPACE, ' '),
            (t.CHAR, 't'),
            (t.CHAR, 'o'),
            (t.WHITESPACE, ' '),
            (t.CHAR, 's'),
            (t.CHAR, 'e'),
            (t.CHAR, 'e'),
            ], 'click <link url="http://here.com">here</link> to see'),
        ([
            (t.LINK_URL, 'http://www.asdf.com'),
            ], '<link url="http://www.asdf.com">http://www.asdf.com</link>'),
        ([
            (t.CHAR, 'x'),
            (t.SUPERSCRIPT_START, '^^'),
            (t.CHAR, '2'),
            (t.SUPERSCRIPT_END, '^^'),
            (t.CHAR, '+foo'),
            ], 'x<super>2</super>+foo'),
        ([
            (t.CHAR, 'x'),
            (t.SUBSCRIPT_START, '~~'),
            (t.CHAR, '2'),
            (t.SUBSCRIPT_END, '~~'),
            (t.CHAR, '+foo'),
            ], 'x<sub>2</sub>+foo'),
        ([
            (t.CHAR, 'some'),
            (t.INDEX_START, '[['),
            (t.CHAR, 'indexed'),
            (t.WHITESPACE, '   '),
            (t.CHAR, 'still'),
            (t.INDEX_END, ']]'),
            (t.CHAR, 'barf'),
            ], 'some<index name="indexed still"/>barf'),
        ([
            (t.CHAR, 'this'),
            (t.WHITESPACE, ' '),
            (t.CHAR, 'becomes'),
            (t.WHITESPACE, ' '),
            (t.ESCAPE, '\\'),
            (t.STRONG_START, '**'),
            (t.CHAR, 'bold'),
            (t.ESCAPE, '\\'),
            (t.STRONG_END, '**'),
            (t.CHAR, '.'),
            ], 'this becomes **bold**.'),
        ]

    def test_helper(self):
        for tokens, result in self.helper_tests:
            tokens = [Token(kind, text) for kind, text in tokens]
            ph = Interpreter(tokens)
            ph.parse()
            xml = ph.dom.toxml()
            xml = '\n'.join(xml.split('\n')[1:])
            xml = xml.strip()
            self.assertEquals(xml, '<p>'+result+'</p>')

   

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InterpreterTest))
    suite.addTest(unittest.makeSuite(ParserTest))
    return suite

def main():
    unittest.TextTestRunner(verbosity=2).run(test_suite())

if __name__ == '__main__':
    main()

