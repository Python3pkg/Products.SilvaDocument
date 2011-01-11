# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Acquisition import aq_chain

from zope import component
from zope.publisher.browser import TestRequest

from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_id

from Products.SilvaDocument.transform import Transformer
from Products.SilvaDocument.transform.base import Context

from Products.Silva.testing import FunctionalLayer, TestCase
from Products.Silva.tests.helpers import open_test_file


KUPU_TABLE_HTML="""
<table _silva_type="plain" _silva_origin="table" _silva_columns="2" _silva_column_info="L:1 L:1" class="plain" cellpadding="0" cellspacing="3" cols="2" width="100%">
 <tbody>
  <tr class="odd">
   <th class="align-left" colspan="2" align="left" width="50%">
    <p class="normal">
     Header cell
    </p>
   </th>
  </tr>
  <tr class="even">
   <td class="align-left" align="left" width="50%">
    <p class="normal">
     Cell one
    </p>
   </td>
   <td class="align-left" align="left" width="50%">
    <p class="normal">
     Cell two
    </p>
   </td>
  </tr>
 </tbody>
</table>
"""

SILVA_TABLE_HTML="""
<table column_info="L:1 L:1" type="plain" columns="2">
 <row>
  <field colspan="2" fieldtype="th">
   <p type="normal">
    Header cell
   </p>
  </field>
 </row>
 <row>
  <field fieldtype="td">
   <p type="normal">
    Cell one
   </p>
  </field>
  <field fieldtype="td">
   <p type="normal">
    Cell two
   </p>
  </field>
 </row>
</table>
"""

KUPU_TABLE_LINK_HTML="""
<table _silva_type="plain" _silva_origin="table" _silva_columns="2" _silva_column_info="L:1 L:1" class="plain" cellpadding="0" cellspacing="3" cols="2" width="100%%">
 <tbody>
  <tr class="odd">
   <th class="align-left" colspan="2" align="left" width="50%%">
    <p class="normal">
     Header cell
    </p>
   </th>
  </tr>
  <tr class="even">
   <td class="align-left" align="left" width="50%%">
    <p class="normal">
     Link to:
     <a title="One" _silva_reference="new" _silva_target="%s">Cell One</a>
    </p>
   </td>
   <td class="align-left" align="left" width="50%%">
    <p class="normal">
     Link to:
     <a title="Two" href="http://infrae.com">Cell Two</a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
"""

SILVA_TABLE_LINK_HTML = """
<table column_info="L:1 L:1" type="plain" columns="2">
 <row>
  <field colspan="2" fieldtype="th">
   <p type="normal">
    Header cell
   </p>
  </field>
 </row>
 <row>
  <field fieldtype="td">
   <p type="normal">
    Link to:
    <link target="" reference="%s" title="One">
     Cell One
    </link>
   </p>
  </field>
  <field fieldtype="td">
   <p type="normal">
    Link to:
    <link url="http://infrae.com" target="" title="Two">
     Cell Two
    </link>
   </p>
  </field>
 </row>
</table>
"""

KUPU_TABLE_IMAGE_HTML="""
<table _silva_type="plain" _silva_origin="table" _silva_columns="1" _silva_column_info="L:1 L:1" class="plain" cellpadding="0" cellspacing="3" cols="1" width="100%%">
 <tbody>
  <tr class="odd">
   <th class="align-left" align="left" width="50%%">
    <p class="normal">
     Header cell
    </p>
   </th>
  </tr>
  <tr class="even">
   <td class="align-left" align="left" width="50%%">
    <p class="normal">
     Chocobo:
     <img src="chocobo.jpg" alt="Chocobo" _silva_reference="new" _silva_target="%s" />
     (Limited edition).
    </p>
   </td>
  </tr>
 </tbody>
</table>
"""

SILVA_TABLE_IMAGE_HTML="""
<table column_info="L:1 L:1" type="plain" columns="1">
 <row>
  <field fieldtype="th">
   <p type="normal">
    Header cell
   </p>
  </field>
 </row>
 <row>
  <field fieldtype="td">
   <p type="normal">
    Chocobo:
   </p>
   <image reference="%s" alignment="" title="Chocobo">
   </image>
   <p type="normal">
    (Limited edition).
   </p>
  </field>
 </row>
</table>

"""


class KupuTransformerTablesTestCase(TestCase):
    """Test transformation from Kupu of tables.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addImage(
            'chocobo', 'Chocobo', file=open_test_file('chocobo.jpg', globals()))

        self.transformer = Transformer.EditorTransformer(editor='kupu')
        self.context = Context(
            self.root.document.get_editable(), TestRequest())

    def test_simple_table(self):
        """Simple table to source.
        """
        result = self.transformer.to_source(
            targetobj=KUPU_TABLE_HTML,
            context=self.context).asBytes('utf-8')
        self.assertXMLEqual(result, SILVA_TABLE_HTML)

    def test_table_with_links(self):
        """Table containing links.
        """
        result = self.transformer.to_source(
            targetobj=KUPU_TABLE_LINK_HTML % get_content_id(self.root.folder),
            context=self.context).asBytes('utf-8')

        version = self.root.document.get_editable()
        service = component.getUtility(IReferenceService)
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 1)
        reference = references[0]
        self.assertEqual(reference.target, self.root.folder)
        self.assertEqual(aq_chain(reference.target), aq_chain(self.root.folder))
        self.assertEqual(reference.source, version)
        self.assertEqual(aq_chain(reference.source), aq_chain(version))

        self.assertXMLEqual(result, SILVA_TABLE_LINK_HTML % reference.tags[1])

    def test_table_with_images(self):
        """Table containing images.
        """
        result = self.transformer.to_source(
            targetobj=KUPU_TABLE_IMAGE_HTML % get_content_id(self.root.chocobo),
            context=self.context).asBytes('utf-8')

        version = self.root.document.get_editable()
        service = component.getUtility(IReferenceService)
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 1)

        reference = references[0]
        self.assertEqual(reference.target, self.root.chocobo)
        self.assertEqual(
            aq_chain(reference.target),
            aq_chain(self.root.chocobo))
        self.assertEqual(reference.source, version)
        self.assertEqual(aq_chain(reference.source), aq_chain(version))

        self.assertXMLEqual(result, SILVA_TABLE_IMAGE_HTML % reference.tags[1])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(KupuTransformerTablesTestCase))
    return suite

