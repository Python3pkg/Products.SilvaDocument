# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.8 $
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

from Products.SilvaDocument.search import Search, HeuristicSearch

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
                result.append('<a class="index-element" name="%s">' %
                              mangle.entities(child.getAttribute('name')))
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
                result.append(mangle.entities(child.data))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'index':
                result.append('<a class="index-element" name="%s">' %
                              mangle.entities(child.getAttribute('name')))
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
        st = mangle.String.inputConvert(st, preserve_whitespace=1)
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
        st = mangle.String.reduceWhitespace(st)

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
        st = mangle.String.inputConvert(st, preserve_whitespace=1)
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
        st = mangle.String.inputConvert(st)
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


class ParserError(Exception):
    pass

class Token:
    
    EMPHASIS_START = 10
    EMPHASIS_END = 11
    STRONG_START = 12
    STRONG_END = 13
    UNDERLINE_START = 14
    UNDERLINE_END = 15

    SUPERSCRIPT_START = 20
    SUPERSCRIPT_END = 21
    SUBSCRIPT_START = 22
    SUBSCRIPT_END = 23

    LINK_START = 50
    LINK_SEP = 51
    LINK_END = 52
    LINK_URL = 54
    LINK_TARGET = 55

    INDEX_START = 60
    INDEX_END = 61
    
    WHITESPACE = 90
    SOFTBREAK = 91
    ESCAPE = 92
    
    CHAR = 100

    def __init__(self, kind, text, callback=None):
        self.kind = kind
        self.text = text
        self.callback = callback

    def __len__(self):
        return len(self.text)

    def __cmp__(self, other):
        return cmp(self.text, other.text)
    
    def __str__(self):
        return self.text

    def __repr__(self):
        return "<%s-%i>" % (self.text, self.kind)

    def select(self):
        if callable(self.callback):
            self.callback()


class ParserState:

    def __init__(self, text, consumed, tokens):
        self.text = text
        self.text_length = len(text)
        self.consumed = consumed
        self.tokens = tokens

    def __repr__(self):
        return "<ParserState: %r>" % self.tokens


class Parser(HeuristicSearch):

    def __init__(self, text):
        problem = ParserState(text, 0, [])
        Search.__init__(self, problem)
        self.initialize_patterns()
        
    def _get_childs(self, node):
        matches = []
        for pattern, token_id in self.patterns:
            m = pattern.match(node.text[node.consumed:])
            if m is None:
                continue
            t = Token(token_id, m.group(1))
            tokens = node.tokens[:]
            tokens.append(t)
            p = ParserState(node.text, node.consumed + len(t.text), tokens)
            matches.append(p)
        return matches
    
    def isTarget(self, node):
        if node.consumed != node.text_length:
            return 0
        p = Interpreter(node.tokens)
        try:
            p.parse()
        except ParserError:
            return 0
        #node.parsed = p
        return 1

    def heuristic(self, node):
        # the more consumed the better
        # the fewer tokens the better
        tokens = float(len(node.tokens))
        consumed = float(node.consumed)
        if consumed == 0 or tokens == 0:
            # XXX: how can this happen anyway??
            # for all tokens, consumed: tokens <= consumed
            # -> max(tokens/consumed) = 1
            # -> returning > 1
            return 10
        token_kinds = [ t.kind for t in node.tokens ]
        kind_sum = reduce(operator.add, token_kinds)
        h = (kind_sum//10)/10.0/tokens + tokens/consumed
        return h

    def initialize_patterns(self):
        patterns = [
            (r'(\+\+)[^\s]', Token.EMPHASIS_START),
            (r'(\+\+)([^A-Za-z0-9]|$)', Token.EMPHASIS_END),
            
            (r'(\*\*)[^\s]', Token.STRONG_START),
            (r'(\*\*)([^A-Za-z0-9]|$)', Token.STRONG_END),
            
            (r'(__)[^\s]', Token.UNDERLINE_START),
            (r'(__)([^A-Za-z0-9]|$)', Token.UNDERLINE_END),
           
            (r'(\^\^)', Token.SUPERSCRIPT_START),
            (r'(\^\^)', Token.SUPERSCRIPT_END),
            
            (r'(~~)', Token.SUBSCRIPT_START),
            (r'(~~)', Token.SUBSCRIPT_END),
           
            (r'(\[\[)', Token.INDEX_START),
            (r'(\]\])([^A-Za-z0-9]|$)', Token.INDEX_END),
           
            (r'(\(\()', Token.LINK_START),
            (r'(\|)', Token.LINK_SEP),
            (r'(\)\))', Token.LINK_END),
            (r'((([^(|)]+)?)(@|mailto\:|(news|(ht|f)tp(s?))\://)[^(|)]+)',
                Token.LINK_URL),
           
            (r'([\n\r]+)', Token.SOFTBREAK),
            (r'([ \t\f\v]+)', Token.WHITESPACE),
            #(r'(\\)', Token.ESCAPE),
            (r'([A-Za-z0-9]+)', Token.CHAR), # catch for long text
            (r'([^A-Za-z0-9 \t\f\v\r\n])', Token.CHAR),
            ]
        self.patterns = []
        for pattern_str, token_id in patterns:
            self.patterns.append((re.compile(pattern_str), token_id))

    def getResult(self):
        return self.results[0]

class Interpreter:
    """parse the tokens to a dom

        be *very* pedantic
    """

    _inline_preceeding_map = {
        '(': ')',
        '[': ']',
        '{': '}',
        '<': '>',
        '"': '"',
        "'": "'",
        ' ': None,
        '-': None,
        '/': None,
        ':': None,
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.dom = ParsedXML('temp', '<p/>')
        self.initialize_rulesets()
        # inline markup nodes: **, ++, __ :
        self._inline_nodes = []
        self.ruleset = 'default'
       
    def parse(self):
        current_node = self.dom.firstChild
        for token in self.tokens:
            current_node = self.handle_token(token, current_node)
            if current_node is None or current_node == self.dom:
                raise ParserError, "Too many close tokens"
        if current_node != self.dom.firstChild:
            raise ParserError, "Not enough close tokens"
        self.validate()
        
    def handle_token(self, token, node):
        ruleset = self.rules[self.ruleset]
        token_handler = ruleset.get(token.kind, None)
        if not callable(token_handler):
            raise ParserError, "Invalid token %r" % token
        return token_handler(token, node)

    def initialize_rulesets(self):
        self.rules = {}
        default_rules = {
            Token.STRONG_START: self.strong_start,
            Token.STRONG_END: self.strong_end,
            Token.EMPHASIS_START: self.emphasis_start,
            Token.EMPHASIS_END: self.emphasis_end,
            Token.UNDERLINE_START: self.underline_start,
            Token.UNDERLINE_END: self.underline_end,
            Token.SUPERSCRIPT_START: self.superscript_start,
            Token.SUPERSCRIPT_END: self.superscript_end,
            Token.SUBSCRIPT_START: self.subscript_start,
            Token.SUBSCRIPT_END: self.subscript_end,
            Token.LINK_START: self.link_start,
            Token.LINK_SEP: self.link_sep,
            Token.LINK_URL: self.link_url,
            Token.LINK_END: self.link_end,
            Token.INDEX_START: self.index_start,
            Token.SOFTBREAK: self.softbreak,
            Token.WHITESPACE: self.whitespace,
            Token.CHAR: self.text,
        }
        self.rules['default'] = default_rules
        
        link_target = {
            Token.CHAR: self.text,
            Token.LINK_END: self.link_end,
        }
        self.rules['link-target'] = link_target

        index = {
            Token.WHITESPACE: self.index_text,
            Token.CHAR: self.index_text,
            Token.INDEX_END: self.index_end,
        }
        self.rules['index'] = index

    def validate(self):
        self._validate_inline_nodes()

    def _validate_inline_nodes(self):
        # XXX maybe this can be done easier?
        for node in self._inline_nodes:
            corresponding_char = None
            # test start node
            prev = node.previousSibling
            next = node.firstChild
            if prev is None:
                # starts the text block -> ok
                pass
            elif (prev.nodeType == prev.ELEMENT_NODE and 
                    prev in self._inline_nodes):
                # it is an inline node -> ok
                pass
            elif prev.nodeType == prev.TEXT_NODE:
                last_char = prev.nodeValue[-1]
                if self._inline_preceeding_map.has_key(last_char):
                    # there is a valid char preceeding, remember 
                    # corresponding_char, if it is not None the char following
                    # must match corresponding_char
                    corresponding_char = self._inline_preceeding_map[
                        last_char]
                else:
                    raise ParserError, "Invalid char %s preceeding "\
                        "inline markup start node" % last_char
            else:
                raise ParserError,\
                    "Invalid token preceeding inline markup start node"
            if next is None:
                raise ParserError,\
                    "No text between start end end markup node"
            if next.nodeType == next.TEXT_NODE and next.nodeValue[0] == ' ':
                raise ParserError,\
                    "Inline markup start nodes must be followed "\
                    "non-whitespace"
            # test end node
            prev = node.lastChild
            next = node.nextSibling
            if prev.nodeType == prev.TEXT_NODE and prev.nodeValue[-1] == ' ':
                raise ParserError, "Inline markup end nodes must be "\
                    "preceeded by non-whitespace"
            if next is not None and next.nodeType == next.TEXT_NODE:
                first_char = next.nodeValue[0]
                if corresponding_char and corresponding_char != first_char:
                    raise ParserError, "wrong corresponding char"
                if first_char not in ' .,;!?\\':
                    raise ParserError, "Wrong char following end node"

    def _get_text_node(self, node):
        if node.nodeType == node.TEXT_NODE:
            return node
        last_child = node.lastChild
        if (last_child is not None and 
                last_child.nodeType != last_child.TEXT_NODE):
            last_child = None
        if last_child is None:
            last_child = node.appendChild(
                self.dom.createTextNode(''))
        return last_child
   
    def _start_inline(self, token, node, node_name):
        self._fail_if_open(node, node_name)
        inline_node = node.appendChild(self.dom.createElement(node_name))
        self._inline_nodes.append(inline_node)
        return inline_node

    def _end_inline(self, token, node, node_name):
        inline_node = node
        if node_name != inline_node.nodeName:
            raise ParserError, "Invalid nesting while </%s>" % node_name
        return inline_node.parentNode

    def _fail_if_open(self, node, node_name):
        test_node = node
        while test_node:
            if test_node.nodeName == node_name:
                raise ParserError, "<%s> already open" % node_name
            test_node = test_node.parentNode
   
    def text(self, token, node):
        text_node = self._get_text_node(node)
        text_node.appendData(token.text)
        return node

    def whitespace(self, token, node):
        text_node = self._get_text_node(node)
        text_node.appendData(' ') # whitespace is normalised
        return node

    def softbreak(self, token, node):
        # softbreak is empty
        node.appendChild(self.dom.createElement('br'))
        return node

    def strong_start(self, token, node):
        return self._start_inline(token, node, 'strong')
        
    def strong_end(self, token, node):
        return self._end_inline(token, node, 'strong')

    def emphasis_start(self, token, node):
        return self._start_inline(token, node, 'em')
        
    def emphasis_end(self, token, node):
        return self._end_inline(token, node, 'em')
       
    def underline_start(self, token, node):
        return self._start_inline(token, node, 'underline')
        
    def underline_end(self, token, node):
        return self._end_inline(token, node, 'underline')

    def link_start(self, token, node):
        return self._start_inline(token, node, 'link')

    def link_sep(self, token, node):
        if node.nodeName != 'link':
            raise ParserError, "LINK_SEP out of link"
        if node.hasAttribute('url'):
            self.ruleset = 'link-target'
        return node
    
    def link_url(self, token, node):
        if node.nodeName == 'link':
            node.setAttribute('url', token.text)
        else:
            link_node = node.appendChild(self.dom.createElement('link'))
            link_node.setAttribute('url', token.text)
            link_node.appendChild(self.dom.createTextNode(token.text))
        return node
   
    def link_target(self, token, node):
        target = ''
        if node.hasAttribute('target'):
            target = node.getAttribute('target')
        node.setAttribute('target', target + token.text)
        return node
    
    def link_end(self, token, node):
        self.ruleset = 'default'
        return self._end_inline(token, node, 'link')
        
    def superscript_start(self, token, node):
        self._fail_if_open(node, 'super')
        self._fail_if_open(node, 'sub')
        return node.appendChild(self.dom.createElement('super'))

    def superscript_end(self, token, node):
        return self._end_inline(token, node, 'super')
    
    def subscript_start(self, token, node):
        self._fail_if_open(node, 'sub')
        self._fail_if_open(node, 'super')
        return node.appendChild(self.dom.createElement('sub'))

    def subscript_end(self, token, node):
        return self._end_inline(token, node, 'sub')
 
    def index_start(self, token, node):
        self.ruleset = 'index'
        return node.appendChild(self.dom.createElement('index'))

    def index_text(self, token, node):
        name = ''
        if node.hasAttribute('name'):
            name = node.getAttribute('name')
        if token.kind == token.WHITESPACE:
            text = ' '
        else:
            text = token.text
        node.setAttribute('name', name + text)
        return node

    def index_end(self, token, node):
        self.ruleset = 'default'
        return node.parentNode

