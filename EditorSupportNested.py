# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.14 $
from __future__ import nested_scopes
import re
import operator
from sys import exc_info
from StringIO import StringIO
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.ParsedXML.ParsedXML import ParsedXML

from Products.Silva import SilvaPermissions
from Products.Silva import mangle

from Products.SilvaDocument.silvaparser import PParser, HeadingParser


class EditorSupport(SimpleItem):
    """XML editor support. """
    
    security = ClassSecurityInfo()

    meta_type = 'Silva Editor Support Service'

    def __init__(self, id):
        self.id = id

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_text_as_html')
    def render_text_as_html(self, node, show_index=0):
        """Render textual content as HTML.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(mangle.entities(child.nodeValue))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('<strong>')
                result.append(self.render_text_as_html(child))
                result.append('</strong>')
            elif child.nodeName == 'em':
                result.append('<em>')
                result.append(self.render_text_as_html(child))
                result.append('</em>')
            elif child.nodeName == 'super':
                result.append('<sup>')
                result.append(self.render_text_as_html(child))
                result.append('</sup>')
            elif child.nodeName == 'sub':
                result.append('<sub>')
                result.append(self.render_text_as_html(child))
                result.append('</sub>')
            elif child.nodeName == 'link':
                result.append('<a href="%s"' %
                              mangle.entities(child.getAttribute('url')))
                if child.getAttribute('target'):
                    result.append(' target="%s"' %
                              mangle.entities(child.getAttribute('target')))
                result.append('>')
                result.append(self.render_text_as_html(child))
                result.append('</a>')
            elif child.nodeName == 'underline':
                result.append('<u>')
                result.append(self.render_text_as_html(child))
                result.append('</u>')
            elif child.nodeName == 'index':
                index = mangle.entities(child.getAttribute('name'))
                result.append('<a class="index-element" name="%s">' %
                    index)
                if show_index:
                    result.append('[[%s]]' % index)
                result.append('</a>')
            elif child.nodeName == 'br':
                result.append('<br />')
            else:
                result.append('<span class="error">%s</span> ' % 
                    self.render_text_as_html(child))
        return ''.join(result)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_heading_as_html')
    def render_heading_as_html(self, node):
        """Render heading content as HTML.
        """
        return self.render_text_as_html(node)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_text_as_editable')
    def render_text_as_editable(self, node):
        """Render textual content as editable text.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(mangle.entities(child.nodeValue))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('**')
                result.append(self.render_text_as_editable(child))
                result.append('**')
            elif child.nodeName == 'em':
                result.append('++')
                result.append(self.render_text_as_editable(child))
                result.append('++')
            elif child.nodeName == 'super':
                result.append('^^')
                result.append(self.render_text_as_editable(child))
                result.append('^^')
            elif child.nodeName == 'sub':
                result.append('~~')
                result.append(self.render_text_as_editable(child))
                result.append('~~')
            elif child.nodeName == 'link':
                result.append('((')
                result.append(self.render_text_as_editable(child))
                result.append('|')
                result.append(mangle.entities(child.getAttribute('url')))
                if child.getAttribute('target'):
                    result.append('|')
                    result.append(mangle.entities(child.getAttribute('target')))
                result.append('))')
            elif child.nodeName == 'underline':
                result.append('__')
                result.append(self.render_text_as_editable(child))
                result.append('__')
            elif child.nodeName == 'index':
                result.append('[[')
                result.append(mangle.entities(child.getAttribute('name')))
                result.append(']]')
            elif child.nodeName == 'br':
                result.append('\n')
            else:
                result.append('ERROR %s ERROR ' % 
                    self.render_text_as_editable(child))
                #raise EditorSupportError, ("Unknown element: %s" % 
                #    child.nodeName
        return ''.join(result)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_heading_as_editable')
    def render_heading_as_editable(self, node):
        """Render textual content as editable text.
        """
        return self.render_text_as_editable(node)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'replace_text')
    def replace_text(self, node, st, parser=PParser):
        """'Parse' the markup to XML. Instead of tokenizing this method uses
        Regular Expressions, which do not make it more neat but do improve
        simplicity.
        """
        # since we don't use Formulator we get UTF8 from the forms, so encode
        # manually here
        st = mangle.String.inputConvert(st, preserve_whitespace=1)
        p = parser(st)
        p.run()
        newdom = p.getResult().parsed.dom
       
        node = node._node
        doc = node.ownerDocument
       
        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        for child in newdom.childNodes:
            self._replace_helper(doc, node, child)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'replace_pre')
    def replace_pre(self, node, st):
        """Add the pre element to the dom

        Don't have to much work here, since no markup is allowed
        """
        # since we don't use Formulator we get UTF8 from the forms, so encode
        # manually here
        # use input convert 2, since the 'normal' one strips whitespace
        st = mangle.String.inputConvert(st, preserve_whitespace=1)
        st = mangle.entities(st)
        st = self._unifyLineBreak(st)
        node = node._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        node.appendChild(doc.createTextNode(st))

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'replace_heading')
    def replace_heading(self, node, st):
        """'Parse' the markup into XML using regular expressions
        """
        self.replace_text(node, st, parser=HeadingParser)

    def _replace_helper(self, doc, node, newdoc):
        """Method to recursively add all children of newdoc to node. Used by 
        replace_text and replace_heading
        """
        for child in newdoc.childNodes:
            if child.nodeType == child.TEXT_NODE:
                newnode = doc.createTextNode(child.nodeValue)
                node.appendChild(newnode)
            elif child.nodeType == child.ELEMENT_NODE:
                newnode = doc.createElement(child.nodeName)
                for i in range(child.attributes.length):
                    newnode.setAttribute(child.attributes.item(i).name, 
                        child.attributes.item(i).value)
                node.appendChild(newnode)
                self._replace_helper(doc, newnode, child)

    security.declarePublic('replace_xml_entities')
    def replace_xml_entities(self, text):
        """Replace all disallowed characters with XML-entities"""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        
        return text


    def _unifyLineBreak(self, data):
        """returns data with unambigous line breaks, i.e only \n.

            This is done by guessing... :)
        """
        if data.find('\n') == -1 and data.find('\r') > -1:
            # looks like mac
            return data.replace('\r', '\n')
        else:
            # looks like windows
            return data.replace('\r', '')
        # looks like unix :)
        return data

InitializeClass(EditorSupport)

def manage_addEditorSupport(container):
    "editor support service factory"
    id = 'service_editorsupport'
    container._setObject(id, EditorSupport(id))

