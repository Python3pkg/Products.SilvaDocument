# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py,v 1.1.2.2.10.2 2004/05/24 20:28:43 zagy Exp $

from Interface import Interface, Attribute


class IToken(Interface):

    kind = Attribute("(int) classifies the token")
    text = Attribute("(unicode) chunk of text the token represents")
  

class ISilvaParserToken(IToken):
    
    openclose = Attribute("defines if the token is an opening (1), "
        "closing (-1) or neither (0)")
    isNesting = Attribute("evaluates to False if token is not nestable, "
        "evaluaes to True otherwise")
    

class IParserState(Interface):
    """State of parsing"""
    
    tokens = Attribute("""sequence of IToken representing the 
        consumed text""")
    parsed = Attribute("(xml dom) DOM of the interpreted state (ususally set"
        " by the parser")
    
    def toxml():
        """returns xml representation of parsed node (self.parsed)

            returns unicode 
            raises ValueError if no interptreted state was found
        """

    def valid():
        """pre-flight check of parser state
        
        return False if state would not result in something interpretable, 
            this means the state will be rejected
        return True otherwise
    
        """
           
class ISilvaParserState(IParserState):
    """state of parsing silva markup"""
    
    text = Attribute("complete text to parse and interpret")
    text_length = Attribute("len(text)")
    consumed = Attribute("already consumed, i.e. parsed portion of text")
    parent = Attribute("previous ParserState")
    kindsum = Attribute("the sum of token ids in self.tokens")
           
           
class IHeuristicsNode(Interface):

    hval = Attribute("""float representing the weight of the node;
        the lower the better""")

    def __cmp__(other):
        """compare by heuristic value (i.e. self.hval)"""


class IParser(Interface):
    """Silva Markup Parser"""

    def run():
        """actually  do the parsing
        
        returns None
        """

    def getResult():
        """return result of parsing
        
        returns IParserState
        
        it should/must (XXX) always return a result
        """
        
  
class IInterpreter(Interface):
    """interprets an IParserState"""

    def parse():
        """parse state

            returns None
            rasises InterpreterError if the state cannot be converted to xml
                (i.e. nesting errors or alike)
        
        """

    def toxml():
        """return xml representation of parser state
            
            returns unicode
            raises ValueError if parse was not called or did not finish 
                properly
        """

