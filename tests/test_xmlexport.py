# -*- coding: utf-8 -*-
import os, sys, re
from os.path import join
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

import unittest
    
from Products.Silva.tests import SilvaTestCase
from Products.SilvaDocument.Document import manage_addDocument
from Products.Silva.Ghost import manage_addGhost
from Products.Silva.GhostFolder import manage_addGhostFolder
from Products.Silva.silvaxml import xmlexport
from Products.Silva.Link import manage_addLink
from Products.ParsedXML.ParsedXML import ParsedXML
from DateTime import DateTime

class SetTestCase(SilvaTestCase.SilvaTestCase):
    def test_xml_document_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        manage_addDocument(
            testfolder, 'test_document', 'This is (surprise!) a document')
        doc = testfolder.test_document
        doc_edit = doc.get_editable()
        doc_edit.content = ParsedXML(
            'test_document',
            """<?xml version="1.0" encoding="utf-8"?><doc>
            <node foo="bar">承諾広告＊既に、２億、３億、５億９千万円収入者が続出<node2>boo</node2>
            baz</node></doc>""")
        xmlexport.initializeXMLExportRegistry()
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(testfolder)
        part1, part2, part3, part4, part5, part6, part7, part8 = splittor.split(exporter.exportToString(exportRoot, settings))
        self.assertEquals(part1, '<?xml version="1.0" encoding="utf-8"?>\n<silva xmlns="http://infrae.com/ns/silva" xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" datetime="')
        self.assertEquals(part2, '" path="/root/testfolder" silva_version="%s" url="http://nohost/root/testfolder"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">' % exportRoot.getSilvaProductVersion())
        self.assertEquals(part3, '</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:modificationtime type="datetime">')
        self.assertEquals(part4, '</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:renderer_name/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">')
        self.assertEquals(part5, '</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/index</silva-extra:location><silva-extra:modificationtime type="datetime">')
        self.assertEquals(part6, '</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:renderer_name/><silva-extra:subject/></set></metadata></auto_toc></default><document id="test_document"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is (surprise!) a document</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">')
        self.assertEquals(part7, '</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/test_document</silva-extra:location><silva-extra:modificationtime type="datetime">')
        self.assertEquals(part8, '</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:renderer_name/><silva-extra:subject/></set></metadata><doc:doc>\n            <doc:node foo="bar">\xe6\x89\xbf\xe8\xab\xbe\xe5\xba\x83\xe5\x91\x8a\xef\xbc\x8a\xe6\x97\xa2\xe3\x81\xab\xe3\x80\x81\xef\xbc\x92\xe5\x84\x84\xe3\x80\x81\xef\xbc\x93\xe5\x84\x84\xe3\x80\x81\xef\xbc\x95\xe5\x84\x84\xef\xbc\x99\xe5\x8d\x83\xe4\xb8\x87\xe5\x86\x86\xe5\x8f\x8e\xe5\x85\xa5\xe8\x80\x85\xe3\x81\x8c\xe7\xb6\x9a\xe5\x87\xba<doc:node2>boo</doc:node2>\n            baz</doc:node></doc:doc></content></document></content></folder></silva>')

    def test_xml_document_with_source_export(self):
        try:
            self.installExtension('SilvaExternalSources')
        except:
            return
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        source_file = open('data/test_csv.csv', 'r')
        testfolder.manage_addProduct[
            'SilvaExternalSources'].manage_addCSVSource(
            'csv',
            'A CSV Source',
            source_file
            )
        manage_addDocument(
            testfolder, 'test_document', 'This is (surprise!) a document')
        doc = testfolder.test_document
        doc_edit = doc.get_editable()
        doc_edit.content = ParsedXML(
            'test_document',
            """<?xml version="1.0" encoding="utf-8"?><doc>
            <source id="csv">
            <parameter key="csvtableclass">grid</parameter>
            <parameter key="csvbatchsize">2</parameter>
            </source>
            </doc>""")
        BatchStart = {'b_start':2}
        Request = testfolder.csv.REQUEST
        Request.form.update(BatchStart)
        xmlexport.initializeXMLExportRegistry()
        settings = xmlexport.ExportSettings()
        settings.setExternalRendering(True)
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(testfolder)
        xml1, xml2 = exporter.exportToString(exportRoot, settings).split('<doc:doc>')
        xml_expected = '\n<doc:sourceid="csv"><doc:parameterkey="csvtableclass">grid</doc:parameter><doc:parameterkey="csvbatchsize">2</doc:parameter><doc:rendered_html><div lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">\n  \n  <div class="listingBar">\n\n      <span class="previous"> \n   <a href="http://nohost/noobject?b_start:int=0">\n          \xc2\xab\n          Previous\n          2 \n          items</a>\n      </span>\n\n\n      \n   \n\n      \n    \n      \n      \n        <a href="http://nohost/noobject?b_start:int=0">1</a>\n      \n\n      \n      \n      <span class="brackets">[</span><span class="currentpage">2</span><span class="brackets">]</span>\n      \n    \n      \n\n      \n    \n      \n      \n      \n      \n \n    </div>\n  <table class="silvatable grid">\n    \n    \n      <thead>\n        <tr>\n          <th>h1</th>\n          <th>h2</th>\n          <th>h3</th>\n          <th>h4</th>\n          <th>h5</th>\n          <th>h6</th>\n        </tr>\n      </thead>\n    <tbody>\n      \n        <tr class="even">\n          <td>r3-1</td>\n          <td>r3-2</td>\n          <td>r3-3</td>\n          <td>r3-4</td>\n          <td>r3-5</td>\n          <td>r3-6</td>\n        </tr>\n      \n \n        <tr class="odd">\n          <td>r4-1</td>\n          <td>r4-2</td>\n          <td>r4-3</td>\n          <td>r4-4</td>\n          <td>r4-5</td>\n       <td>r4-6</td>\n        </tr>\n      \n    </tbody>\n    \n  </table>\n</div>\n</doc:rendered_html></doc:source>\n            </doc:doc></content></document></content></folder></silva>'
        self.assertEquals(xml2.replace(' ',''), xml_expected.replace(' ',''))
            
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite
