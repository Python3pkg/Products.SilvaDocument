# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py,v 1.1.2.2.10.1 2004/04/29 16:57:02 roman Exp $

from Interface import Interface, Attribute


class IParserState(Interface):
    """State of parsing silva markup"""
    
    text = Attribute("complete text to parse and interpret")
    text_length = Attribute("len(text)")
    consumed = Attribute("already consumed, i.e. parsed portion of text")
    tokens = Attribute("""sequence of tokens representing the 
        consumed text""")
    parent = Attribute("previous ParserState")
    kindsum = Attribute("the sum of token ids in self.tokens")
        
    def toxml():
        "returns xml representation of parsed node"

    def valid():
        "return True if state could result in something interpretable"
           
           
class IHeuristicsNode(Interface):

    hval = Attribute("""float representing the weight of the node;
        the lower the better""")

    def __cmp__(other):
        """compare by heuristic value (i.e. self.hval)"""
