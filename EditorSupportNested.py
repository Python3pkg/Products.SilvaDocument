# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import re
from sys import exc_info
from StringIO import StringIO
from xml.parsers.expat import ExpatError

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.ParsedXML.ParsedXML import ParsedXML

from Products.Silva import SilvaPermissions
from Products.Silva.helpers import escape_entities

def _regular_expression_escape(st):
    result = ""
    for c in st:
        result += '\\'+c
    return result        

class EditorSupportError(Exception):
    pass

class EditorSupport(SimpleItem):
    """XML editor support. """
    
    security = ClassSecurityInfo()

    meta_type = 'Silva Editor Support Service'

    _silva_markup = {
        '__': 'underline', 
        '**': 'strong', 
        '++': 'em', 
        '^^': 'super',
        '~~': 'sub',
    }

    _silva_entities = {
        'ast': '*',
        'plus': '+',
        'under': '_',
        'lowbar': '_',
        'caret': '^',
        'tilde': '~',
        'lparen': '(',
        'rparen': ')',
        'lbrack': '[',
        'rbrack': ']',
        'pipe': '|',
        'verbar': '|',
    }
    
    p_MARKUP = re.compile(r"(?P<markup>%s)(?P<text>.*?)(?P=markup)" % (
        '|'.join(map(_regular_expression_escape, _silva_markup.keys())), ),
        re.S)
    p_LINK = re.compile(
        r"^([^<]*|.*>[^\"]*)\({2}(.*?)\|([^|]*?)(\|(.*?))?\){2}",
        re.S)
    p_INDEX = re.compile(r"^([^<]*|.*>[^\"]*)\[{2}(.*?)\|(.*?)\]{2}", re.S)
    
    
    def __init__(self, id):
        self.id = id

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_text_as_html')
    def render_text_as_html(self, node):
        """Render textual content as HTML.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(escape_entities(child.data))
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
                              escape_entities(child.getAttribute('url')))
                if child.getAttribute('target'):
                    result.append(' target="%s"' %
                              escape_entities(child.getAttribute('target')))
                result.append('>')
                result.append(self.render_text_as_html(child))
                result.append('</a>')
            elif child.nodeName == 'underline':
                result.append('<u>')
                result.append(self.render_text_as_html(child))
                result.append('</u>')
            elif child.nodeName == 'index':
                result.append('<a class="index-element" name="%s">' %
                              escape_entities(child.getAttribute('name')))
                result.append(self.render_text_as_html(child))
                result.append('</a>')
            elif child.nodeName == 'br':
                result.append('<br />')
            else:
                result.append('<span class="error">%s</span> ' % 
                    self.render_text_as_html(child))
                #raise EditorSupportError, (
                #   "Unknown element: %s" % child.nodeName)
        return ''.join(result)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_heading_as_html')
    def render_heading_as_html(self, node):
        """Render heading content as HTML.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(escape_entities(child.data))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'index':
                result.append('<a class="index-element" name="%s">' %
                              escape_entities(child.getAttribute('name')))
                result.append(self.render_heading_as_html(child))
                result.append('</a>')
            else:
                raise EditorSupportError, ("Unknown element: %s" % 
                    child.nodeName)
        return ''.join(result)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_text_as_editable')
    def render_text_as_editable(self, node):
        """Render textual content as editable text.
        """
        result = []
        chars_to_entities = self._silva_chars_to_entities
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(chars_to_entities(child.data))
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
                result.append(chars_to_entities(child.getAttribute('url')))
                if child.getAttribute('target'):
                    result.append('|')
                    result.append(chars_to_entities(
                        child.getAttribute('target')))
                result.append('))')
            elif child.nodeName == 'underline':
                result.append('__')
                result.append(self.render_text_as_editable(child))
                result.append('__')
            elif child.nodeName == 'index':
                result.append('[[')
                result.append(self.render_text_as_editable(child))
                result.append('|')
                result.append(chars_to_entities(child.getAttribute('name')))
                result.append(']]')
            #elif child.nodeName == 'person':
            #    result.append('{{')
            #    for subchild in child.childNodes:
            #        result.append(subchild.data)
            #    result.append('}}')
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
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(self._silva_chars_to_entities(child.data))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'index':
                result.append('[[')
                result.append(self.render_heading_as_editable(child))
                result.append('|')
                result.append(child.getAttribute('name'))
                result.append(']]')
            else:
                raise EditorSupportError, ("Unknown element: %s" % 
                    child.nodeName)

        return ''.join(result)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'replace_text')
    def replace_text(self, node, st):
        """'Parse' the markup to XML. Instead of tokenizing this method uses
        Regular Expressions, which do not make it more neat but do improve
        simplicity.
        """
        # since we don't use Formulator we get UTF8 from the forms, so encode
        # manually here
        st = self.input_convert2(st)
        st = self.replace_xml_entities(st)
        st = self._unifyLineBreak(st)
        while 1:
            match = self.p_MARKUP.search(st)
            if not match:
                break
            st = st.replace(match.group(0), u'<%s>%s</%s>' % (
                self._silva_markup[match.group('markup')], 
                    match.group('text'), 
                    self._silva_markup[match.group('markup')]))
        while 1:
            match = self.p_LINK.search(st)
            if not match:
                break
            if match.group(4):
                target = match.group(5)
                if not target:
                    target = '_blank'
                st = st.replace(match.group(0), 
                    u'%s<link url="%s" target="%s">%s</link>' % (
                        match.group(1), 
                        match.group(3), 
                        target, 
                        match.group(2)))
            else:
                st = st.replace(match.group(0), 
                    u'%s<link url="%s">%s</link>' % (
                        match.group(1), 
                        match.group(3), 
                        match.group(2)))
        while 1:
            match = self.p_INDEX.search(st)
            if not match:
                break
            st = st.replace(match.group(0), 
                u'%s<index name="%s">%s</index>' % (
                    match.group(1), 
                    match.group(3), 
                    match.group(2)))
        st = st.replace('\n', '<br/>')
        # reduce whitespace
        st = self.reduce_whitespace(st)

        st = self._replace_silva_entities(st)
        node = node._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        newdom = self.create_dom_forgiving(doc, st)
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
        st = self.input_convert2(st)
        st = self.replace_xml_entities(st)
        st = self._unifyLineBreak(st)
        st = self._replace_silva_entities(st)
        node = node._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        newdom = self.create_dom_forgiving(doc, st)
        for child in newdom.childNodes:
            self._replace_helper(doc, node, child)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'replace_heading')
    def replace_heading(self, node, st):
        """'Parse' the markup into XML using regular expressions
        """
        st = self.input_convert(st)
        st = self.replace_xml_entities(st)
        st = self._unifyLineBreak(st)
        reg_i = re.compile(r"\[{2}(.*?)\|(.*?)\]{2}", re.S)
        while 1:
            match = reg_i.search(st)
            if not match:
                break
            st = st.replace(match.group(0), u'<index name="%s">%s</index>' % (
                match.group(2), match.group(1)))

        st = self._replace_silva_entities(st)
        node = node._node
        doc = node.ownerDocument
        while node.hasChildNodes():
            node.removeChild(node.firstChild)
        newdom = self.create_dom_forgiving(doc, st)

        for child in newdom.childNodes:
            self._replace_helper(doc, node, child)

    def _replace_helper(self, doc, node, newdoc):
        """Method to recursively add all children of newdoc to node. Used by 
        replace_text and replace_heading
        """
        for child in newdoc.childNodes:
            if child.nodeType == 3:

                newnode = doc.createTextNode(child.nodeValue)
                node.appendChild(newnode)
            elif child.nodeType == 1:
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

    def _replace_silva_entities(self, text):
        for name, rep in self._silva_entities.items():
            # mind that we've already replaced the XML entities, so we 
            # should be looking at '&amp;<name>;' instead of '&<name>;'
            text = text.replace('&amp;%s;' % name, rep)
        return text

    def _silva_chars_to_entities(self, text):
        for name, rep in self._silva_entities.items():
            text = text.replace(rep, '&%s;' % name)
        return text

    security.declarePrivate('create_dom_forgiving')
    def create_dom_forgiving(self, doc, st):
        """When creating a domtree from the text goes wrong because of illegal
        markup, this method removes ALL occurrences of the tag where it went
        wrong.  XXX This is rather rigorous, could we remove only the tag which
        is actually illegal? 
        """
        # ParsedXML requires UTF8 encoded strings
        st = st.encode('utf8')
        elements = ['a', 'strong', 'em', 'underline', 'sub', 'sup']
        while 1:
            try:
                dom = ParsedXML('temporary', '<p>%s</p>' % st)
                return dom
            except ExpatError, message:
                message = str(message)
                text = st
                match = re.search('line [0-9]+, column ([0-9]+)', message)
                # the line number always seems to be 1
                char = int(match.group(1))
                # now find the illegal tag
                foundlines = 1
                text = text[char:]
                # expat seems to sometimes return a number a little lower 
                # than the index of the start of the tag,
                # so walk to the next tag
                while not text or text[0] != '<':
                    if not text:
                        # this should not happen, but just in case respond 
                        # to it by raising the exception again
                        raise ExpatError
                    text = text[1:]
                # check wether it's an opening or closing tag
                if text[1] == '/':
                    text = text[2:]
                else:
                    text = text[1:]
                # now check which type of tag this is
                found = 0
                for el in elements:
                    if text[:len(el)] == el:
                        breakingel = el
                        # and remove all elements of that type
                        st = re.sub('<\/?%s.*?>' % el, '', st)
                        found = 1
                # this is nessecary so multiple errors can be dealt with
                if found == 1:
                    continue
                # we should never get here, but if we would somehow, we'd 
                # get into an endless loop, avoid that by raising the 
                # previous error
                raise ExpatError, message

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

