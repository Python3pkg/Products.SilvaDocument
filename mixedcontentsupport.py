# Copyright (c) 2002-2006 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.13 $
# Python
from __future__ import nested_scopes
import re
from xml.sax.saxutils import escape, unescape, quoteattr
from urlparse import urlparse

from zope.interface import implements
# Zope
import Acquisition
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.SilvaDocument import interfaces
from Products.Silva.adapters.path import getPathAdapter

URL_PATTERN = r'(((http|https|ftp|news)://([A-Za-z0-9%\-_]+(:[A-Za-z0-9%\-_]+)?@)?([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+)(:[0-9]+)?(/([A-Za-z0-9\-_\?!@#$%^&*/=\.]+[^\.\),;\|])?)?|(mailto:[A-Za-z0-9_\-\.]+@([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+))'
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
    
    implements(interfaces.IMixedContentSupport)

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
    
class ParagraphSupport(MixedContentSupport):
    """ Mixed content support for SilvaDocument paragraphs.
    """
    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'parse')
    def parse(self, inputstr):
        """ Parse input string to a DOM
        """
        from sprout.silvasubset import PARAGRAPH_SUBSET

        inputstr = unicode(inputstr, 'UTF-8')
        node = self._node
        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        PARAGRAPH_SUBSET.filteredParse(inputstr, node)

        # we have to convert absolute link href and image src paths relative
        # to the current virtual host root so they become relative to the
        # Zope root 
        self._convertPaths(node)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'renderHTML')
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
            elif child.nodeName == 'abbr':
                result.append('<abbr')
                if child.getAttribute('title'):
                    result.append(
                        ' title="%s"' % child.getAttribute('title'))
                result.append('>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</abbr>')
            elif child.nodeName == 'acronym':
                result.append('<acronym')
                if child.getAttribute('title'):
                    result.append(
                        ' title="%s"' % child.getAttribute('title'))
                result.append('>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</acronym>')
            elif child.nodeName == 'link':
                path = child.getAttribute('url')
                url = self._linkHelper(node, path)                
                result.append('<a href="%s"' %  mangle.entities(url))
                if child.hasAttribute('target'):
                    target = child.getAttribute('target')
                    if target == '': target = '_blank'
                    result.append(
                        ' target="%s"' % mangle.entities(target))
                result.append('>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</a>')
            elif child.nodeName == 'underline':
                result.append('<u>')
                result.append(self._renderHtmlHelper(child, view_type))
                result.append('</u>')
            elif child.nodeName == 'index':
                name = child.getAttribute('name')
                result.append('<a class="index-element" name="%s">' % name)
                # In nested lists and tables we cannot rely on the
                # correct view_type passed in, so check for edit_mode
                # from the request.
                edit_mode = node.REQUEST.get('edit_mode', 0)
                if edit_mode:
                    result.append('[[%s]]' % name)
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
                result.append(child.nodeValue)
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('<b>')
                result.append(self._renderEditableHelper(child))
                result.append('</b>')
            elif child.nodeName == 'em':
                result.append('<i>')
                result.append(self._renderEditableHelper(child))
                result.append('</i>')
            elif child.nodeName == 'super':
                result.append('<sup>')
                result.append(self._renderEditableHelper(child))
                result.append('</sup>')
            elif child.nodeName == 'sub':
                result.append('<sub>')
                result.append(self._renderEditableHelper(child))
                result.append('</sub>')
            elif child.nodeName == 'abbr':
                if child.getAttribute('title'):
                    result.append(
                        '<abbr title="%s">' % child.getAttribute('title'))
                else:
                    result.append('<abbr>')
                result.append(self._renderEditableHelper(child))
                result.append('</abbr>')
            elif child.nodeName == 'link':
                url = mangle.entities(child.getAttribute('url'))
                if not urlparse(url)[0]:
                    # we have a path, convert
                    pad = getPathAdapter(child.REQUEST)
                    url = pad.pathToUrlPath(url)
                if child.hasAttribute('target'):
                    target = child.getAttribute('target')
                    if target == '': target = '_blank'
                else:
                    target = mangle.entities(child.getAttribute('target'))
                linktext = self._renderEditableHelper(child)
                if target:
                    tag = '<a href="%s" target="%s">' % (url, target)
                else:
                    tag = '<a href="%s">' % url
                result.append(tag)
                result.append(linktext)
                result.append('</a>')
            elif child.nodeName == 'underline':
                result.append('<u>')
                result.append(self._renderEditableHelper(child))
                result.append('</u>')
            elif child.nodeName == 'index':
                result.append('<index>')
                result.append(mangle.entities(child.getAttribute('name')))
                result.append('</index>')
            elif child.nodeName == 'acronym':
                if child.getAttribute('title'):
                    result.append(
                        '<acronym title="%s">' % child.getAttribute('title'))
                else:
                    result.append('<acronym>')
                result.append(self._renderEditableHelper(child))
                result.append('</acronym>')
            elif child.nodeName == 'abbr':
                result.append('<abbr>')
                if child.getAttribute('title'):
                    result.append(
                        ' title="%s"' % child.getAttribute('title'))
                result.append(self._renderEditableHelper(child))
                result.append('</acronym>')
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

    def _convertPaths(self, node):
        """convert URL paths to absolute physical ones"""
        links = node.getElementsByTagName('link')
        for link in links:
            url = link.getAttribute('url')
            if not urlparse(url)[0]:
                # we have a path
                pad = getPathAdapter(node.REQUEST)
                path = pad.urlToPath(url)
                link.setAttribute('url', path)

InitializeClass(ParagraphSupport)

class HeadingSupport(ParagraphSupport):
    """ Mixed content support for SilvaDocument headings
    """
    
    security = ClassSecurityInfo()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'parse')
    def parse(self, inputstr):
        """ Parse input string to a DOM
        """
        from sprout.silvasubset import HEADING_SUBSET

        inputstr = unicode(inputstr, 'UTF-8')
        node = self._node
        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        HEADING_SUBSET.filteredParse(inputstr, node)

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
