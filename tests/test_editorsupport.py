# Copyright (c) 2002, 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_editorsupport.py,v 1.13.4.3 2003/12/23 08:20:24 zagy Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

import unittest
from xml.dom.minidom import parseString

from Products.SilvaDocument.silvaparser import \
    Token, PParser, Interpreter
from Products.SilvaDocument.EditorSupportNested import EditorSupport


class PParserTest(unittest.TestCase):

    large_text = """Kaum standen am folgenden Tage die hohen Felsengipfel im Glanz des Sonnenlichts, so hŸpfte Gustav aus dem Bette und fand - wem kommt dabey nicht das ehemahls selbst genossene kindische EntzŸcken beym Anblick des Weihnachtsgeschenks ins GedŠchtniss? - einen netten Anzug auf dem Stuhle am Bette, den die Gattinn des Schultheissen von den Sšhnen eines im Flecken wohnenden Edelmannes, einstweilen angenommen hatte, da sich nicht so schnell, als sie es jetzt wŸnschte, die NŠhnadeln zu Buchenthal in Bewegung setzen liessen. Ewalds hatten ein Weilchen auf das Benehmen des kleinen Lieblings gelauscht, und šffneten das Gemach, als sich eben seine Empfindungen in ein lautes ÈAch wie schšn!Ç auflšsten. ÈGuten Tag, Papa, guten Tag, Mama!Ç schluchzte Gustav, und eilte den Kommenden entgegen, um mit tausend HŠndekŸssen ihnen Dank und Liebe zu zollen. Die guten Alten staunten bey dem seltenen FeingefŸhl eines so kleinen Knaben, und hŠtten von diesem Augenblicke gegen die SchŠtze von Golconda, dem aufgenommenen Pflegling nicht entsagt. Die muthigen Apfelschimmel stampften schon ungeduldig im Hofe den Boden. Gustav stack geschwind mit Ewalds HŸlfe in dem ganz passenden Anzuge, und glich einem jungen Liebesgott, indess die Gattin des Schultheissen alle die kleinen hŠuslichen Angelegenheiten und die GeschŠfte des Tages an das Gesinde austheilte, ihm nochmahls Achtsamkeit und Fleiss empfahl, genoss Gustav eine wohlschmeckende Milchsuppe, denn Caffee kam selten, bloss bey ganz ausnehmenden FŠllen, in Ewalds Haus, weil diese Leute einen gewissen edlen Stolz im Entsagen allen dessen, was das Ausland zeugte, suchten, und sich genŸgsam an das, was auf heimathlichem Boden wuchs, hielten. Auch kannte Ewald lebende Beyspiele genug, dass Neigung und Geschmack an dem, das Blut in Wallung setzenden - und schlecht gekocht, den Magen schlaff machenden - Caffee sich beym weiblichen Geschlechte so leicht in Leidenschaft umwandle, als beym mŠnnlichen die Liebe zum Schnaps. Seine Familie zŠhlte einige unglŸckliche Beweise dieses Satzes, die dem wohlwollenden Manne eine unumstšssliche Abneigung gegen diese Schote einflšssten, obschon seine škonomische Lage ihm allenfalls auch heutigen Tages, wo Caffee so ungemein gestiegen ist, dass man ihn kaum bezahlen kann - gestattet hŠtte, denselben ohne deutsche Mengsel und sonstige HŸlfsmittel, die Caffee heissen, ohne es zu seyn, zwey Mahl tŠglich zu geniessen. DŠchten und handelten doch alle Deutsche wie Ewald! Zehnmahl hatte die geschŠftige Alte alle nšthigen Befehle schon gegeben, und eben so oft noch eine Kleinigkeit nachzuholen. Jetzt suchte sie einen SchlŸssel, den sie in den HŠnden hielt, dann einen Pelzmantel, den sie im Juny doch gewiss nicht nšthig hatte. Ewald lŠchelte und ging an den Wagen. Das gute Hausweib hatte, obschon es nahe an den Sechzigen stand, noch keinen vollen Tag die PfŠhle im Stich gelassen, in denen es von Jugend auf lebte und webte; bloss Theilnahme und Liebe zu Gustav, konnte es zu diesem Entschluss bewegen. Endlich kam sie mit zwey Schachteln von ziemlichem Umfange voll Victualien, eine Magd folgte mit einem dito Sack, und hinten auf dem Wagen blšckten zwey festgebundene Hammel um baldige Entlassung aus so lŠssigen Fesseln. Die Hofhunde bellten zum Abschiede, Hans schwang die Peitsche, und pfeilschnell flogen die ungeduldigen Apfelschimmel zum Flecken hinaus. GlŸck auf den Weg!"""
    complicated_paras = [
""" Op 25 november 2003 is de CGE&Y Strategy Award, de prijs voor de beste
universitaire scriptie op het gebied van strategisch management,
uitgereikt aan drs. Carolien Heemskerk, afgestudeerd bedrijfskundige aan
de Rotterdam School of Management van de Erasmus Universiteit Rotterdam.""",
"""De voormalig studente ontvangt voor de award een geldprijs van
vijfduizend euro, haar begeleider prof.dr. Henk W. Volberda heeft
vanwege zijn succesvolle begeleiding van deze scriptie
vijfentwintighonderd euro gewonnen.
Van de door Nederlandse universiteiten genomineerde scripties blinkt de
scriptie met als titel Disaggregating the firm by means of Business
Process Outsourcing uit op toekomstgerichtheid, diepgang en
theoretische onderbouwing. Carolien Heemskerk gaat in haar scriptie diep
in op meerdere modellen die organisaties kunnen ontvlechten. Zij heeft
vooral de complexe theorie kunnen kanaliseren tot een pragmatisch
toepasbare ontvlechting. Deze scriptie heeft voor bedrijven die
ontvlechting overwegen grote toegevoegde waarde. Het is inspirerend voor
de praktijk van strategisch management, aldus drs. P.F. Segaar,
voorzitter van de zevenhoofdige jury.
De universiteiten van Nederland hebben twaalf scripties genomineerd voor
de Strategy Award. De deskundige jury onder voorzitterschap van drs.
P.F. Segaar (zelfstandig bestuurs- en organisatieadviseur, voormalig
directeur Strategie Aegon N.V.) bepaalde na meerdere juryronden dat vijf
scripties in aanmerking kwamen voor deze prijs. De kwaliteit van de
scripties met de titels Disaggregating the firm by means of Business
Process Outsourcing (Erasmus Universiteit Rotterdam, Rotterdam School
of Management, vakgroep Strategie en Omgeving), Co-operative Technology
Roadmapping (TU Delft), Tussen Droom en Daad (Rijksuniversiteit
Groningen), Waardecreatie en waarde toe-eigening door ondernemingen:
een increasing Returns perspectief (Erasmus Universiteit Rotterdam) en
E-business en de waardeketen (Rijksuniversiteit Groningen) leidde tot
een uitgebreide discussie binnen de jury. Na een vier uur durend beraad
waarin de meningen van de juryleden fors uiteen liepen, werd door de
jury uiteindelijk unaniem besloten dat de beste scriptie op het gebied
van strategisch management geschreven is door Carolien Heemskerk. De
kwaliteit van de scripties is dit jaar bijzonder hoog. Het was voor de
jury dan ook kiezen tussen scripties met een zeer hoog niveau waarin de
kleine details mee gingen tellen, lichtte de juryvoorzitter toe tijdens
de uitreiking die plaatsvond op het Nationale Strategie Congres.
Het Nationale Strategie Congres en de uitreiking van de Strategy Award
zijn georganiseerd door de Vereniging voor Strategische Beleidsvorming
(VSB) en Cap Gemini Ernst & Young. Volgend jaar wordt wederom door de
Vereniging voor Strategische Beleidsvorming het uitreiken van de
Strategy Award georganiseerd.
De VSB is sinds 1971 HET Nederlandse platform voor strategie met ruim
450 aangesloten leden afkomstig uit het bedrijfsleven, de overheid, de
universitaire wereld of werkend als strategisch adviseur. Naast een
sterk netwerk in het bedrijfsleven heeft de VSB nauw contact met de
universitaire wereld.
Voor meer informatie zie www.strategie-vsb.nl
Jurysamenstelling""",
"""De jury is gevormd door een vertegenwoordiging uit het bedrijfsleven en
de academische wereld met zowel een technische als een
managementachtergrond:
dr. P.R. Broholm, Theodoor Gilissen Bankiers;
drs. Ph. Waalewijn RM, Universitair hoofddocent Marketing, Erasmus
Universiteit Rotterdam;
drs. ing. W.J.F. Kels, voormalig directeur Strategische planning ING;
prof.dr.ir. J.W. Koolhaas, TU Delft;
prof.dr. J. Strikwerda, Nolan Norton & Company;
ir. R.W. van der Reijden MBA, manager production, RDM Technology.
Onder voorzitterschap van:
drs. P.F. Segaar, zelfstandig bestuurs- en organisatieadviseur,
voormalig directeur Strategie Aegon N.V."""]
    
    def test_simpleemph(self):
        parser = PParser("++foobar++      blafasel")
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
        parser = PParser("*****")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 3)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].text, '*')
        self.assertEquals(t[2].kind, Token.STRONG_END)
       
    def test_boldasterix2(self):
        parser = PParser("******")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 4)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].text, '*')
        self.assertEquals(t[3].kind, Token.STRONG_END)
      
    def test_italicplus(self):
        parser = PParser("+++++")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 3)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].text, '+')
        self.assertEquals(t[2].kind, Token.EMPHASIS_END)

    def test_bolditalic(self):
        parser = PParser("**++foobar++**")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 5)
        self.assertEquals(t[0].kind, Token.STRONG_START)
        self.assertEquals(t[1].kind, Token.EMPHASIS_START)
        self.assertEquals(t[3].kind, Token.EMPHASIS_END)
        self.assertEquals(t[4].kind, Token.STRONG_END)
       
    def test_italicbold(self):
        parser = PParser("++**foobar**++")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 5)
        self.assertEquals(t[0].kind, Token.EMPHASIS_START)
        self.assertEquals(t[1].kind, Token.STRONG_START)
        self.assertEquals(t[3].kind, Token.STRONG_END)
        self.assertEquals(t[4].kind, Token.EMPHASIS_END)
       
    def test_underline(self):
        parser = PParser("__i am underlined__")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 7)
        self.assertEquals(t[0].kind, Token.UNDERLINE_START)
        self.assertEquals(t[6].kind, Token.UNDERLINE_END)
         
    def test_underline2(self):
        parser = PParser("__under**lined and **bold** and st__uff__")
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
            parser = PParser(text)
            parser.run()
            t = parser.getResult().tokens
            self.assertEquals(len(t), length)

    def test_url(self):
        urls = [
            'http://www.asdf.com',
            'mailto:foo@bar.com',
            'ftp://bla.fasel/',
            'https://asdf.com/blablubb/sdfa/df/dfa?sdfasd=434&ds=ddf%20#foo'
        ]
        for url in urls:
            parser = PParser(url)
            parser.run()
            t = parser.getResult().tokens
            self.assertEquals(len(t), 1, "%r -> %r" % (url, t))
            t = t[0]
            self.assertEquals(t.kind, t.LINK_URL)
            self.assertEquals(t.text, url)
            
    def _test_urls(self, texts, url):
        for text, length, url_at in texts:
            p = PParser(text)
            p.run()
            t = p.getResult().tokens
            self.assertEquals(len(t), length, "%d != %d in %r -> %r" % (
                len(t), length, text, t))
            self.assertEquals(t[url_at].kind, Token.LINK_URL)
            self.assertEquals(t[url_at].text, url)

    def test_url2(self):
        texts = [
            ("(see http://www.x.yz)", 5, 3),
            ("software got smarter: http://www.x.yz.", 9, 7),
            ("at http://www.x.yz, but", 6, 2),
            ("(see ((foo|http://www.x.yz)))", 9, 6),
            ]
        url = "http://www.x.yz"
        self._test_urls(texts, url)

    def test_url3(self):
        texts = [
            ("(see http://www.x.yz/)", 5, 3),
            ("software got smarter: http://www.x.yz/.", 9, 7),
            ("at http://www.x.yz/, but", 6, 2),
            ("(see ((foo|http://www.x.yz/)))", 9, 6),
            ]
        url = "http://www.x.yz/"
        self._test_urls(texts, url)
            
    def test_link(self):
        parser = PParser("click ((here|http://here.com)) to see")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 11)
        self.assertEquals(t[2].kind, Token.LINK_START)
        self.assertEquals(t[3].text, 'here')
        self.assertEquals(t[4].kind, Token.LINK_SEP)
        self.assertEquals(t[5].kind, Token.LINK_URL)
        self.assertEquals(t[6].kind, Token.LINK_END)

    def test_morelinks(self):
        # mainly a speed test
        parser = PParser("""Once upon a time, users had to learn markup (see ((http://www.x.yz|http://www.x.yz))).
Then, software got smarter: ((http://www.x.yz|http://www.x.yz)).
Now, it could be called intelligent. You see this at ((http://www.x.yz|http://www.x.yz)), but
sometimes it's too smart for its own good.
Users think it's dumb.""")
        parser.run()
        

    def test_linktarget(self):
        parser = PParser("click ((here|http://here.com|_top)) to see")
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

    def test_linktarget2(self):
        parser = PParser("((slashdot|http://www.slashdot.org|foo))")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 7)
        self.assertEquals(t[0].kind, Token.LINK_START)
        self.assertEquals(t[1].text, 'slashdot')
        self.assertEquals(t[2].kind, Token.LINK_SEP)
        self.assertEquals(t[3].kind, Token.LINK_URL)
        self.assertEquals(t[4].kind, Token.LINK_SEP)
        self.assertEquals(t[5].text, 'foo')
        self.assertEquals(t[6].kind, Token.LINK_END)
        
    def test_linktarget3(self):
        parser = PParser("((slashdot|http://www.slashdot.org|))")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 6)
        self.assertEquals(t[0].kind, Token.LINK_START)
        self.assertEquals(t[1].text, 'slashdot')
        self.assertEquals(t[2].kind, Token.LINK_SEP)
        self.assertEquals(t[3].kind, Token.LINK_URL)
        self.assertEquals(t[4].kind, Token.LINK_SEP)
        self.assertEquals(t[5].kind, Token.LINK_END)

    def test_linkwithbraces(self):
        parser = PParser("click ((Journal & Books|simple?field_search=reference_type:(journal%20book))) to see")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 29)
        self.assertEquals(t[24].kind, Token.LINK_END)

    def test_linkparen(self):
        parser = PParser("(((issue tracker|http://issues.infrae.com/silva/issue678)))")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(t[0].kind, Token.PARENTHESIS_OPEN)
        self.assertEquals(t[0].text, '(')
        self.assertEquals(t[-1].kind, Token.PARENTHESIS_CLOSE)
        self.assertEquals(t[-1].text, ')')

    def test_superscriptbold(self):
        parser = PParser("**foo^^bar^^**")
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
        parser = PParser("a~~1~~^^2^^+a~~2~~^^2^^=a~~3~~^^2^^")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 23)
        self.assertEquals(t[0].text, 'a')
        self.assertEquals(t[1].kind, Token.SUBSCRIPT_START)
        self.assertEquals(t[3].kind, Token.SUBSCRIPT_END)
        self.assertEquals(t[4].kind, Token.SUPERSCRIPT_START)
        self.assertEquals(t[6].kind, Token.SUPERSCRIPT_END)

    def test_softbreak(self):
        parser = PParser("a\nb\n\n\n\nc")
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
        parser = PParser(self.large_text)
        parser.run()

    def test_paras(self):
        for p_text in self.complicated_paras:
            p = PParser(p_text)
            p.run()
            
    def test_index(self):
        parser = PParser("A Word[[Word]] blafasel")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 8)
        self.assertEquals(t[3].kind, Token.INDEX_START)
        self.assertEquals(t[5].kind, Token.INDEX_END)


    def test_escape(self):
        parser = PParser("In Silva markup **bold** is marked up as \**bold\**")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(len(t), 23)
        self.assertEquals(t[21].kind, Token.ESCAPE)

    def test_alot(self):
        # speed test, this took > 10 minutes some time ago
        parser = PParser("A paragraph. Which includes **bold**, ++italic++, __underlined__, a ((hyperlink|http://www.infrae.com)), and an index item[[index item]]. But we have more **bold** and ++italic++; even **++bold-italic++** or **__bold-underlinded__**. **++__bold-italic-underlined-superscript__++**.")
        parser.run()
        t = parser.getResult().tokens


    def test_markup_follows_linebreak(self):
        parser = PParser("Afteralinebreak\n++markup++ shouldnotbeignored\n")
        parser.run()
        t = parser.getResult().tokens
        self.assertEquals(t[0].kind, Token.CHAR)
        self.assertEquals(t[0].text, 'Afteralinebreak')
        self.assertEquals(t[1].kind, Token.SOFTBREAK)
        self.assertEquals(t[2].kind, Token.EMPHASIS_START)
        self.assertEquals(t[3].kind, Token.CHAR)
        self.assertEquals(t[3].text, 'markup')
        self.assertEquals(t[4].kind, Token.EMPHASIS_END)
        self.assertEquals(t[5].kind, Token.WHITESPACE)
        self.assertEquals(t[6].kind, Token.CHAR)
        # should the last linebreak be stripped?
        self.assertEquals(t[7].kind, Token.SOFTBREAK)
        self.assertEquals(len(t), 8)
       


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
        ([
            (t.CHAR, 'click'),
            (t.WHITESPACE, ' '),
            (t.LINK_START, '(('),
            (t.CHAR, 'here'),
            (t.LINK_SEP, '|'),
            (t.LINK_URL, 'http://www.asdf.com'),
            (t.LINK_END, '))'),
            ], 'click <link url="http://www.asdf.com">here</link>'),
        ([
            (t.CHAR, 'click'),
            (t.WHITESPACE, ' '),
            (t.LINK_START, '(('),
            (t.CHAR, 'here'),
            (t.LINK_SEP, '|'),
            (t.CHAR, '../foo'),
            (t.LINK_END, '))'),
            ], 'click <link url="../foo">here</link>'),
        ([
            (t.ESCAPE, '\\'),
            (t.LINK_START, '(('),
            ], '(('),
        ([
            (t.CHAR, "(see"),
            (t.WHITESPACE, " "),
            (t.LINK_START, '(('),
            (t.CHAR, 'xyz'),
            (t.LINK_SEP, '|'),
            (t.LINK_URL, 'http://www.x.yz'),
            (t.LINK_END, '))'),
            (t.CHAR, ')'),
            ], '(see <link url="http://www.x.yz">xyz</link>)'),
        ([
            (t.LINK_START, "(("),
            (t.CHAR, 'slashdot'),
            (t.LINK_SEP, '|'),
            (t.LINK_URL, 'http://slashdot.org'),
            (t.LINK_SEP, '|'),
            (t.CHAR, 'foo'),
            (t.LINK_END, '))'),
            ], '<link url="http://slashdot.org" target="foo">slashdot</link>'),
        ([
            (t.LINK_START, "(("),
            (t.CHAR, 'slashdot'),
            (t.LINK_SEP, '|'),
            (t.LINK_URL, 'http://slashdot.org'),
            (t.LINK_SEP, '|'),
            (t.LINK_END, '))'),
            ], '<link url="http://slashdot.org" target="_blank">slashdot</link>'),
        ]

    def test_helper(self):
        for tokens, result in self.helper_tests:
            tokens = [Token(kind, text) for kind, text in tokens]
            ph = Interpreter(tokens)
            ph.parse()
            xml = ph.dom.toxml()
            expected_xml = parseString('<p>'+result+'</p>').toxml()
            self.assertEquals(xml, expected_xml)

class EditableTest(unittest.TestCase):

    def test_escape(self):
        
        cases = [
            ('foobar', 'foobar'),
            ('<em>foobar</em>', '++foobar++'),
            ('<strong>foobar</strong>', '**foobar**'),
            ('<strong>foo<em>bar</em></strong>', '**foo++bar++**'),
            ('<strong>**</strong>', '**\\****'),
            ('((a+b)*c)', '\\((a+b)*c)'),
            ('((a+b*c))', '\\((a+b*c\\))'),
            ('<strong>bold</strong> is **bold**', '**bold** is \\**bold\\**'),
            ('<link url="http://slashdot.org">slashdot</link>',
                '((slashdot|http://slashdot.org))'),
            ('<link url="http://slashdot.org" target="foo">slashdot</link>',
                '((slashdot|http://slashdot.org|foo))'),
            ('<link url="http://slashdot.org" target="_blank">slashdot</link>',
                '((slashdot|http://slashdot.org|))'),
            ('<link url="http://slashdot.org">http://slashdot.org</link>',
                'http://slashdot.org'),
        ]
        
        es = EditorSupport('')
        
        for xml_text, expected_editable in cases:
            dom = parseString('<p>%s</p>' % xml_text)
            editable = es.render_text_as_editable(dom.firstChild)
            self.assertEquals(expected_editable, editable,
                '%s was converted to %s, instead of %s' % (xml_text,
                    editable, expected_editable))

    def test_render_links(self):
        es = EditorSupport('')
        cases = [
            ('foobar', 'foobar'),
            ('foo http://www.x.yz', 'foo <a href="http://www.x.yz">http://www.x.yz</a>'),
            ('foo http://www.x.yz, and', 'foo <a href="http://www.x.yz">http://www.x.yz</a>, and'),
            ('foo http://www.x.yz/ bla foo', 'foo <a href="http://www.x.yz/">http://www.x.yz/</a> bla foo'),
            ('foo http://www.x.yz, http://zxy.abc bla', 'foo <a href="http://www.x.yz">http://www.x.yz</a>, <a href="http://zxy.abc">http://zxy.abc</a> bla'),
           ]
        for editable, expected_html in cases:
            html = es.render_links(editable)
            self.assertEquals(expected_html, html,
                '%s was converted to %s, instead of %s' % (editable,
                    html, expected_html))
            
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InterpreterTest))
    suite.addTest(unittest.makeSuite(PParserTest))
    suite.addTest(unittest.makeSuite(EditableTest))
    return suite

def main():
    from hotshot import Profile
    p = Profile('paras.hotshot')
    unittest.TextTestRunner(verbosity=2).run(test_suite())

if __name__ == '__main__':
    try:
        from hotshot import Profile
        p = Profile('editorsupport.hotshot')
        p.runcall(framework)
    except ImportError:
        framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    main()
    
