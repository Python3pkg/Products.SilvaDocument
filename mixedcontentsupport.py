# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1.4.1 $
# Python
from __future__ import nested_scopes
import re
import operator
from sys import exc_info
from StringIO import StringIO
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
# Zope
import Acquisition
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.ParsedXML.ParsedXML import ParsedXML
# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
# Silva Document
from Products.SilvaDocument.silvaparser import \
    PParser, HeadingParser, LinkParser, URL_PATTERN
    
from Products.SilvaDocument import externalsource    
from Products.SilvaDocument import interfaces

# from silvaparser, thanks to zagy:
_url_match = re.compile(URL_PATTERN)

class SupportRegistry:
    def __init__(self, default_class):
        self._mapping = {(None, None): default_class}

    def register(self, meta_type, element_name, class_):
        self._mapping[(meta_type, element_name)] = class_

    def registerDefault(self, class_):
        self.register(None, None, class_)

    def registerElementDefault(self, element_name, class_):
        self.register(None, element_name, class_)

    def registerMetaTypeDefault(self, meta_type, class_):
        self.register(meta_type, None, class_)

    def lookupByName(self, meta_type, element_name):
        mapping = self._mapping
        result = mapping.get((meta_type, element_name))
        if result is not None:
            return result
        result = mapping.get((meta_type, None))
        if result is not None:
            return result
        result = mapping.get((None, element_name))
        if result is not None:
            return result
        return mapping.get((None, None))

    def lookup(self, context=None, node=None):
        if context is None:
            meta_type = None
        else:
            meta_type = context.meta_type
        if node is None:
            nodename = None
        else:
            nodename = node.nodeName
        return self.lookupByName(meta_type, nodename)

class MixedContentSupport(Acquisition.Explicit):
    """ Abstract base class for mixed content support.
    """
    
    __implements__ = interfaces.IMixedContentSupport, 

    _escapes = [
        ('\\', '\\\\'),
        ('**', '\\*\\*'),
        ('++', '\\+\\+'),
        ('__', '\\_\\_'),
        ('~~', '\\~\\~'),
        ('^^', '\\^\\^'),
        ('((', '\\(\\('),
        ('))', '\\)\\)'),
        ('[[', '\\[\\['),
        (']]', '\\]\\]'),]
    
    _additional_escape = {
        'strong': '*',
        'em': '+',
        'link': '(',
        'super': '^',
        'sub': '~',
        'underline': '_',
        'index': '[',
    }

    def __init__(self, node):
        self._node = node
        
    def _editableToDOM(self, editablestr, parser):
        """convert editable to dom"""
        parser = parser(editablestr)
        parser.run()
        return parser.getResult().parsed.dom
        
    def _insertDOM(self, doc, node, newdoc):
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
                self._insertDOM(doc, newnode, child)
    
    def escape_text(self, text):
        for replace, with in self._escapes:
            text = text.replace(replace, with)
        return text

    def escape_text_node(self, node):
        parent_name = node.parentNode.nodeName
        node_text = node.nodeValue
        node_text = self.escape_text(node_text)
        escape_too = self._additional_escape.get(parent_name)
        if not escape_too:
            return node_text
        if node_text.startswith(escape_too):
            node_text = '\\' + node_text
        return node_text
        
class ParagraphSupport(MixedContentSupport):
    """ Mixed content support for SilvaDocument paragraphs.
    """
    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'parse')
    def parse(self, inputstr):
        """ Parse input string to a DOM
        """
        # Since we don't use Formulator we get UTF8 from the forms,
        # so decode to unicode manually here.
        inputstr = unicode(inputstr, 'utf-8')
        newdom = self._editableToDOM(inputstr, PParser)
        node = self._node
        doc = node.ownerDocument
       
        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
            
        # insert new node
        for child in newdom.childNodes:
            self._insertDOM(doc, node, child)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'renderHTML')
    def renderHTML(self, view_type='public'):
        """ Render textual content as HTML.
        """
        return self._renderHtmlHelper(self._node, view_type)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'renderEditable')
    def renderEditable(self):
        """ Render textual content as editable text.
        """
        return self._renderEditableHelper(self._node)
    
    def _renderHtmlHelper(self, node, view_type):
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(mangle.entities(child.nodeValue))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('<strong>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</strong>')
            elif child.nodeName == 'em':
                result.append('<em>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</em>')
            elif child.nodeName == 'super':
                result.append('<sup>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</sup>')
            elif child.nodeName == 'sub':
                result.append('<sub>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</sub>')
            elif child.nodeName == 'link':
                path = child.getAttribute('url')
                url = self._linkHelper(node, path)                
                result.append('<a href="%s"' %  mangle.entities(url))
                pass
                if child.getAttribute('target'):
                    result.append(
                        ' target="%s"' %
                        mangle.entities(child.getAttribute('target')))
                result.append('>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</a>')
            elif child.nodeName == 'underline':
                result.append('<u>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</u>')
            elif child.nodeName == 'index':
                index = mangle.entities(child.getAttribute('name'))
                result.append(
                    '<a class="index-element" name="%s">' % index)
                if view_type == 'edit':
                    result.append('[[%s]]' % index)
                result.append('</a>')
            elif child.nodeName == 'br':
                result.append('<br />')
            else:
                result.append('<span class="error">%s</span> ' % 
                    self._renderHtmlHelper(child, view_type))
        return ''.join(result)
    
    def _renderEditableHelper(self, node):
        """Render textual content as editable text.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(self.escape_text_node(child))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('**')
                result.append(self._renderEditableHelper(child))
                result.append('**')
            elif child.nodeName == 'em':
                result.append('++')
                result.append(self._renderEditableHelper(child))
                result.append('++')
            elif child.nodeName == 'super':
                result.append('^^')
                result.append(self._renderEditableHelper(child))
                result.append('^^')
            elif child.nodeName == 'sub':
                result.append('~~')
                result.append(self._renderEditableHelper(child))
                result.append('~~')
            elif child.nodeName == 'link':
                url = mangle.entities(child.getAttribute('url'))
                url_comparator = mangle.entities(
                    self._linkHelper(node, child.getAttribute('url')))
                target = mangle.entities(child.getAttribute('target'))
                linktext = self._renderEditableHelper(child)
                if (not target and linktext == url_comparator):
                    result.append(url)
                else:
                    result.append('((')
                    result.append(linktext)
                    result.append('|')
                    result.append(url)
                    if target:
                        result.append('|')
                        result.append(target)
                    result.append('))')
            elif child.nodeName == 'underline':
                result.append('__')
                result.append(self._renderEditableHelper(child))
                result.append('__')
            elif child.nodeName == 'index':
                result.append('[[')
                result.append(mangle.entities(child.getAttribute('name')))
                result.append(']]')
            elif child.nodeName == 'br':
                result.append('\n')
            else:
                result.append(
                    'ERROR %s ERROR ' % self._renderEditableHelper(child))
        return ''.join(result)

    def _linkHelper(self, context, path):
        # If path is empty (can it be?), just return it
        if path == '':
            return path
        # If it is a url already, return it:
        if _url_match.match(path):
            return path
        # Is it a query of anchor fragment? If so, return it
        if path[0] in ['?', '#']:
            return path
        # It is not an URL, query or anchor, so treat it as a path.
        # If it is a relative path, treat is as such:
        if not path.startswith('/'):
            container = context.get_container()
            return container.absolute_url() + '/' + path
        # If it is an absolute path, try to traverse it to
        # a Zope/Silva object and get the URL for that.
        splitpath = [p.encode('ascii','ignore') for p in path.split('/') ]
        obj = context.restrictedTraverse(splitpath, None)
        if obj is None:
            # Was not found, maybe the link is broken, but maybe it's just 
            # due to virtual hosting situations or whatever.
            return path
        if hasattr(obj.aq_base, 'absolute_url'):
            # There are some cases where the object we find 
            # does not have the absolute_url method.
            return obj.absolute_url()
        # In all other cases:
        return path

InitializeClass(ParagraphSupport)

class HeadingSupport(ParagraphSupport):
    """ Mixed content support for SilvaDocument headings
    """
    
    security = ClassSecurityInfo()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'parse')
    def parse(self, inputstr):
        """ Parse input string to a DOM
        """
        # Since we don't use Formulator we get UTF8 from the forms,
        # so decode to unicode manually here.
        inputstr = unicode(inputstr, 'utf-8')
        newdom = self._editableToDOM(inputstr, HeadingParser)
        node = self._node
        doc = node.ownerDocument
       
        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
            
        # insert new node
        for child in newdom.childNodes:
            self._insertDOM(doc, node, child)

InitializeClass(HeadingSupport)            
            
class PreSupport(ParagraphSupport):
    """ Mixed content support for SilvaDocument pre elements
    """

    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'parse')
    def parse(self, inputstr):
        """Add the pre element to the dom

        Don't have to much work here, since no markup is allowed
        """
        # Since we don't use Formulator we get UTF8 from the forms,
        # so decode to unicode manually here.
        inputstr = unicode(inputstr, 'utf-8')
        inputstr = self._unifyLineBreak(inputstr)
        node = self._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        node.appendChild(doc.createTextNode(inputstr))

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'renderEditable')
    def renderEditable(self):
        result = ""
        node = self._node
        for child in node.childNodes:
            assert child.nodeType == child.TEXT_NODE
            assert child.firstChild is None
            result += child.nodeValue
        return result
        
    def _unifyLineBreak(self, inputstr):
        """ Returns data with unambigous line breaks, i.e only \n.
        """
        if inputstr.find('\n') == -1 and inputstr.find('\r') > -1:
            # looks like mac
            return inputstr.replace('\r', '\n')
        else:
            # looks like windows
            return inputstr.replace('\r', '')
        # looks like unix :)
        return inputstr

InitializeClass(PreSupport)
    
class LinkSupport(ParagraphSupport):
    """ Mixed content support for SilvaDocument link elements
    """
    
    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'parse')
    def parse(self, inputstr):
        # Since we don't use Formulator we get UTF8 from the forms,
        # so decode to unicode manually here.
        inputstr = unicode(inputstr, 'utf-8')
        newdom = self._editableToDOM(inputstr, LinkParser)
        node = self._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        node.appendChild(doc.createTextNode(string))

        # insert new node
        for child in newdom.childNodes:
            self._insertDOM(doc, node, child)

InitializeClass(LinkSupport)
