# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: silvaparser.py,v 1.6.4.9 2004/02/06 15:59:47 zagy Exp $
from __future__ import nested_scopes

# python
import re
import operator
from xml.dom.minidom import parseString

# sibling
from Products.SilvaDocument.search import Search, HeuristicSearch
from Products.SilvaDocument.interfaces import IParserState, IHeuristicsNode


def _initialize_patterns(patterns):
    compiled = []
    for pattern_str, token_id in patterns:
        compiled.append((re.compile(pattern_str), token_id))
    return tuple(compiled)

URL_PATTERN = r'(((http|https|ftp|news)://([^:@]+(:[^@]+)?@)?([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+)(/([A-Za-z0-9\-_\?!@#$%^&*()/=\.]+[^\.\),;\|])?)?|(mailto:[A-Za-z0-9_\-\.]+@([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+))'
        
class InterpreterError(Exception):
    pass


class Token:
    """Silva markup tokens"""
    
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
    PARENTHESIS_OPEN = 93
    PARENTHESIS_CLOSE = 94
    
    CHAR = 100

    
    _start_end_map = {
        STRONG_START: STRONG_END,
        EMPHASIS_START: EMPHASIS_END,
        UNDERLINE_START: UNDERLINE_END,
        SUPERSCRIPT_START: SUPERSCRIPT_END,
        SUBSCRIPT_START: SUBSCRIPT_END,
        LINK_START: LINK_END,
        INDEX_START: INDEX_END,
    }
    
    _start_tokens = {
        STRONG_START: 1,
        EMPHASIS_START: 1,
        UNDERLINE_START: 1,
        SUPERSCRIPT_START: 1,
        SUBSCRIPT_START: 1,
        LINK_START: 1,
        INDEX_START: 1,
    }
    
    _end_tokens = {
        STRONG_END: -1,
        EMPHASIS_END: -1,
        UNDERLINE_END: -1,
        SUPERSCRIPT_END: -1,
        SUBSCRIPT_END: -1,
        LINK_END: -1,
        INDEX_END: -1,
    }

    _nesting = {
        PARENTHESIS_OPEN: 1,
        PARENTHESIS_CLOSE: 1,
    }
    _nesting.update(_start_tokens)
    _nesting.update(_end_tokens)

    def __init__(self, kind, text):
        self.kind = kind
        self.text = text
        self.openclose = self._start_tokens.get(kind,
            self._end_tokens.get(kind, 0))
        self.isNesting = self._nesting.get(kind, 0)

    def __len__(self):
        return len(self.text)

    def __cmp__(self, other):
        return cmp(self.text, other.text)
    
    def __str__(self):
        return self.text

    def __repr__(self):
        return "<%r-%i>" % (self.text, self.kind)


class ParserState:
    """State of parsing silva markup"""
    
    __implements__ = IParserState, IHeuristicsNode
    
    def __init__(self, text, consumed, tokens, parent=None):
        self.text = text
        self.text_length = len(text)
        self.consumed = consumed
        self.tokens = tokens
        self.parsed = None
        self.openclose_map = {}
        self.parent = parent
        self.kindsum = 0
        self._valid_state = None
        self.nesting_list = []
        
        openclose = None
        self.parenthesis = 0
        self.factor = 0
        
        new_token = self._new_token()

        if parent is not None:
            openclose = parent.openclose
            self.parenthesis = parent.parenthesis
            self.factor = parent.factor
            self.openclose_map = parent.openclose_map.copy()
            self.kindsum = parent.kindsum
            self.nesting_list = parent.nesting_list[:]
        if openclose is None:
            openclose = reduce(operator.add,
                [t.openclose for t in tokens], 0)
        else:
            if new_token is not None:
                openclose += new_token.openclose
        self.openclose = openclose
        if new_token is not None:
            self.kindsum += new_token.kind
            if new_token.isNesting:
                self.nesting_list.append(new_token)

    def __repr__(self):
        return "<ParserState: %r>" % self.tokens

    def __cmp__(self, other):
        return cmp(self.hval, other.hval)

    def toxml(self):
        # parsed is set externally... 
        if self.parsed is None:
            raise ValueError, "No interpreted state found"
        return self.parsed.toxml()

    def valid(self):
        # returns 0 if self.tokens will not result in something interpretable
        # anyway; this is mainly for speed reasons.
        if self._valid_state is not None:
            return self._valid_state
        if self.openclose < 0:
            self._valid_state = 0
            return 0
        openclose_map = self.openclose_map
        token = self._new_token()
        if token.openclose == 0:
            self._valid_state = 1
            return 1
        kind = token._start_end_map.get(token.kind, token.kind)
        old_val = openclose_map.setdefault(kind, 0)
        new_val = token.openclose + old_val
        if new_val not in (0, 1):
            self._valid_state = 0
            return 0
        openclose_map[kind] = new_val
        self._valid_state = 1
        return 1
            
    def _new_token(self):
        if self.tokens:
            return self.tokens[-1]


class Parser(HeuristicSearch):
    """Parser for silva markup

        
        abstract
    """
    
    children_per_char = 10

    def __init__(self, text):
        problem = ParserState(text, 0, [])
        self.children_generated = 0
        self.max_children = len(text) * self.children_per_char
        self._fallback_node = None
        Search.__init__(self, problem)
        
    def _get_children(self, node):
        matches = []
        text = node.text[node.consumed:]
        for pattern, token_id in self.patterns:
            m = pattern.match(text)
            if m is None:
                continue
            t = Token(token_id, m.group(1))
            tokens = node.tokens[:]
            tokens.append(t)
            p = ParserState(node.text, node.consumed + len(t.text), tokens,
                parent=node)
            if not p.valid():
                continue
            matches.append(p)
            self.children_generated += 1
            if self.children_generated > self.max_children:
                fb = self._generate_fallback_node(node.text)
                self._fallback_node = fb
                matches.append(fb)
        return matches
    
    def isTarget(self, node):
        if node.consumed != node.text_length:
            return 0
        if node.openclose != 0:
            return 0
        p = Interpreter(node.tokens)
        try:
            p.parse()
        except InterpreterError:
            return 0
        node.parsed = p
        return 1

    def heuristic(self, node):
        # Heuristic for choosing nodes:
        # the more text consumed the better
        # the fewer tokens the better
        # the lower the token-kind the better
        if node is self._fallback_node:
            return 0
        tokens = float(len(node.tokens))
        consumed = float(node.consumed)
        kind_sum = node.kindsum
        parenthesis = 1
        if (len(node.tokens) > 1 
                and len(node.nesting_list) > 1
                and node.tokens[-1].kind == Token.PARENTHESIS_CLOSE
                and node.nesting_list[-2].kind == Token.PARENTHESIS_OPEN):
            parenthesis = 0.8
        pattern_badness = 0
        if (len(node.tokens) > 1 and
                node.tokens[-1].kind == Token.PARENTHESIS_OPEN and
                node.tokens[-2].kind == Token.LINK_START):
            # hm, concider it a hack... but (( ( is worse than ( (( ... 
            pattern_badness += 1 
        h = ((int(kind_sum/10))/10.0/tokens + tokens/consumed) * parenthesis + \
            pattern_badness
        #if node.text == "click ((Journal & Books|simple?field_search=reference_type:(journal%20book))) to see":
        #    print h, node.tokens
        #print node.text, node.tokens, h
        return h

    def getResult(self):
        return self.results[0]
    
    def _generate_fallback_node(self, text):
        token = Token(Token.CHAR, text)
        node = ParserState(text, len(text), tokens=[token])
        assert node.valid()
        return node


class PParser(Parser):
    """Parser for silva markup P nodes
    """

    patterns = _initialize_patterns([
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
        (URL_PATTERN, Token.LINK_URL),
       
        (r'([\n\r]+)', Token.SOFTBREAK),
        (r'([ \t\f\v]+)', Token.WHITESPACE),
        (r'(\\)', Token.ESCAPE),
        (r'(\()', Token.PARENTHESIS_OPEN),
        (r'(\))', Token.PARENTHESIS_CLOSE),
        
        (r'([A-Za-z0-9\.\-&;]+)', Token.CHAR), # catch for long text
        (r'([^A-Za-z0-9\.\-&; \t\f\v\r\n()\\])', Token.CHAR),
        ])


class HeadingParser(Parser):
    
    patterns = _initialize_patterns([
        (r'(\+\+)[^\s]', Token.EMPHASIS_START),
        (r'(\+\+)([^A-Za-z0-9]|$)', Token.EMPHASIS_END),
        
        (r'(\^\^)', Token.SUPERSCRIPT_START),
        (r'(\^\^)', Token.SUPERSCRIPT_END),
        
        (r'(~~)', Token.SUBSCRIPT_START),
        (r'(~~)', Token.SUBSCRIPT_END),
          
        (r'(\[\[)', Token.INDEX_START),
        (r'(\]\])([^A-Za-z0-9]|$)', Token.INDEX_END),
       
        (r'([ \t\f\v]+)', Token.WHITESPACE),
        (r'(\\)', Token.ESCAPE),
        (r'([A-Za-z0-9]+)', Token.CHAR), # catch for long text
        (r'([^A-Za-z0-9 \t\f\v\r\n])', Token.CHAR),
        ])


class LinkParser(Parser):

    patterns = _initialize_patterns([
        (URL_PATTERN, Token.LINK_URL),
        (r'([ \t\f\v]+)', Token.WHITESPACE),
        (r'(\\)', Token.ESCAPE),
        (r'([A-Za-z0-9]+)', Token.CHAR), # catch for long text
        (r'([^A-Za-z0-9 \t\f\v\r\n])', Token.CHAR),
        ])


class Interpreter:
    """parse the tokens to a dom

        be *very* pedantic

        The tokens comming in must be corret, otherwise InterpreterError is 
        raised.

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
        # using minidom, it's *much* faster than ParsedXML
        self.dom = parseString('<p/>')
        self.initialize_rulesets()
        # inline markup nodes: **, ++, __ :
        self._inline_nodes = []
        self.ruleset = 'default'
       
    def parse(self):
        current_node = self.dom.firstChild
        for token in self.tokens:
            current_node = self.handle_token(token, current_node)
            if current_node is None or current_node == self.dom:
                raise InterpreterError, "Too many close tokens"
        if current_node != self.dom.firstChild:
            raise InterpreterError, "Not enough close tokens"
        self.validate()
       
    def toxml(self):
        return self.dom.toxml()

    def handle_token(self, token, node):
        ruleset = self.rules[self.ruleset]
        token_handler = ruleset.get(token.kind, None)
        if token_handler is None:
            raise InterpreterError, "Invalid token %r in ruleset %s" % (
                token, self.ruleset)
        if not callable(token_handler):
            raise InterpreterError, \
                "Found handler for token %r, but it's not callable" % token
        return token_handler(token, node)

    def initialize_rulesets(self):
        self.rules = {}
        
        self.rules['default'] = {
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
            Token.LINK_URL: self.link_url_sole,
            Token.INDEX_START: self.index_start,
            Token.ESCAPE: self.escape,
            Token.SOFTBREAK: self.softbreak,
            Token.WHITESPACE: self.whitespace,
            Token.PARENTHESIS_OPEN: self.text,
            Token.PARENTHESIS_CLOSE: self.text,
            Token.CHAR: self.text,
        }

        self.rules['link-text'] = {
            Token.PARENTHESIS_OPEN: self.text,
            Token.PARENTHESIS_CLOSE: self.text,
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
            Token.WHITESPACE: self.whitespace,
            Token.CHAR: self.text,
            Token.LINK_URL: self.text,
            Token.LINK_SEP: self.link_sep_aftertext,
            Token.ESCAPE: self.escape,
        }

        self.rules['link-url'] = {
            Token.PARENTHESIS_OPEN: self.link_url_fromtext,
            Token.PARENTHESIS_CLOSE: self.link_url_fromtext,
            Token.CHAR: self.link_url_fromtext,
            Token.LINK_URL: self.link_url,
            Token.LINK_SEP: self.link_sep_afterurl,
            Token.LINK_END: self.link_end,
        }

        self.rules['link-afterurl'] = {
            Token.LINK_SEP: self.link_sep_afterurl,
            Token.LINK_END: self.link_end,
        }
       
        self.rules['link-target'] = {
            Token.CHAR: self.link_target,
            Token.LINK_END: self.link_end,
        }

        self.rules['index'] = {
            Token.PARENTHESIS_OPEN: self.index_text,
            Token.PARENTHESIS_CLOSE: self.index_text,
            Token.WHITESPACE: self.index_text,
            Token.CHAR: self.index_text,
            Token.INDEX_END: self.index_end,
        }

        self.rules['escape'] = {
            Token.STRONG_START: self.escaped_text,
            Token.STRONG_END: self.escaped_text,
            Token.EMPHASIS_START: self.escaped_text,
            Token.EMPHASIS_END: self.escaped_text,
            Token.UNDERLINE_START: self.escaped_text,
            Token.UNDERLINE_END: self.escaped_text,
            Token.SUPERSCRIPT_START: self.escaped_text,
            Token.SUPERSCRIPT_END: self.escaped_text,
            Token.SUBSCRIPT_START: self.escaped_text,
            Token.SUBSCRIPT_END: self.escaped_text,
            Token.LINK_START: self.escaped_text,
            Token.INDEX_START: self.escaped_text,
            Token.SOFTBREAK: self.escaped_softbreak,
            Token.WHITESPACE: self.escaped_whitespace,
            Token.PARENTHESIS_OPEN: self.escaped_text,
            Token.PARENTHESIS_CLOSE: self.escaped_text,
            Token.CHAR: self.escaped_text,
            Token.ESCAPE: self.escaped_text,
        }
        
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
                    (prev in self._inline_nodes or prev.nodeName == 'br')):
                # it is an inline node -> ok
                # follows a soft break -> ok
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
                    raise InterpreterError, "Invalid char %s preceeding "\
                        "inline markup start node" % last_char
            else:
                raise InterpreterError,\
                    "Invalid token preceeding inline markup start node"
            if next is None:
                raise InterpreterError,\
                    "No text between start end end markup node"
            if next.nodeType == next.TEXT_NODE and next.nodeValue[0] == ' ':
                raise InterpreterError,\
                    "Inline markup start nodes must be followed by "\
                    "non-whitespace"
            # test end node
            prev = node.lastChild
            next = node.nextSibling
            if prev.nodeType == prev.TEXT_NODE and prev.nodeValue[-1] == ' ':
                raise InterpreterError, "Inline markup end nodes must be "\
                    "preceeded by non-whitespace"
            if next is not None and next.nodeType == next.TEXT_NODE:
                first_char = next.nodeValue[0]
                if corresponding_char and corresponding_char != first_char:
                    raise InterpreterError, "wrong corresponding char"
                if first_char not in """ '")]}>-/:.,;!?\\""":
                    raise InterpreterError, \
                        "Wrong char %r following end node </%s>" % (
                            first_char, node.nodeName)

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
            raise InterpreterError, "Invalid nesting while </%s>" % node_name
        return inline_node.parentNode

    def _fail_if_open(self, node, node_name):
        test_node = node
        while test_node:
            if test_node.nodeName == node_name:
                raise InterpreterError, "<%s> already open" % node_name
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
        self.ruleset = 'link-text'
        return self._start_inline(token, node, 'link')

    def link_sep_aftertext(self, token, node):
        if node.nodeName != 'link':
            raise InterpreterError, "LINK_SEP out of link"
        self.ruleset = 'link-url'
        return node
   
    def link_sep_afterurl(self, token, node):
        if node.nodeName != 'link':
            raise InterpreterError, "LINK_SEP out of link"
        node.setAttribute('target', '')
        self.ruleset = 'link-target'
        return node
   
    def link_url(self, token, node):
        self.ruleset = 'link-afterurl'
        node.setAttribute('url', token.text)
        return node
  
    def link_url_sole(self, token, node):
        # this is just a plain url -> text==url
        link_node = node.appendChild(self.dom.createElement('link'))
        link_node.setAttribute('url', token.text)
        link_node.appendChild(self.dom.createTextNode(token.text))
        return node
  
    def link_url_fromtext(self, token, node):
        url = ''
        if node.hasAttribute('url'):
            url = node.getAttribute('url')
        url += token.text
        node.setAttribute('url', url)
        return node
  
    def link_target(self, token, node):
        target = node.getAttribute('target')
        node.setAttribute('target', target + token.text)
        return node
    
    def link_end(self, token, node):
        if node.hasAttribute('target') and node.getAttribute('target') == '':
            node.setAttribute('target', '_blank')
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

    def escape(self, token, node):
        self._pre_escape_ruleset = self.ruleset
        self.ruleset = 'escape'
        return node
    
    def escaped_text(self, token, node):
        self.ruleset = self._pre_escape_ruleset
        return self.text(token, node)
    
    def escaped_whitespace(self, token, node):
        self.ruleset = self._pre_escape_ruleset
        return self.whitespace(token, node)
    
    def escaped_softbreak(self, token, node):
        self.ruleset = self._pre_escape_ruleset
        return self.softbreak(token, node)

