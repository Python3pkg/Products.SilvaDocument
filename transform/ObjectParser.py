"""
module for parsing dom-nodes or strings to an
object tree based on the classes in 'base.py'.

The ObjectParser instance takes an object
that provides 'mappings' via var(object):
names of tags are mapped to objects which
will be instantiated.

Currently only minidom is supported. 


"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.2 $'

from Products.SilvaDocument.transform.base import Element, Frag, Text
import inspect

#
# convert - method wrapper
#           maintains a conversion-stack in the context
# 
class convert_wrapper:
    def __init__(self, forward):
        self.forward = forward

    def __call__(self, node, context):
        print "called"
        if not hasattr(context, 'stack'):
            context.stack = []
        context.stack.append(node)
        res = self.forward(node, context)
        context.stack.pop(node)
        return res

#
# Transformation from Dom to our Nodes
#
class ObjectParser:
    def __init__(self, spec):
        """ initialize ObjectParser with the Element tags
            contained in spec which are later used for
            tagname-to-Object parsing.
        """
        self.spec = spec
        self.typemap = {}
        for x,y in vars(spec).items():
            try:
                if issubclass(y, Element) or issubclass(y, Text):
                    if hasattr(y, 'xmlname'):
                        x = y.xmlname
                    self.typemap[x]=y
                
            except TypeError:
                pass
        
    def parse(self, source):
        """ return xist-like objects parsed from UTF-8 string
            or dom tree.
            
            Fragment contains node objects and unknown a list of unmapped 
            nodes.
        """
        if type(source)==type(u''):
            source = source.encode('UTF8')

        if type(source)==type(''):
            from xml.dom import minidom
            tree = minidom.parseString(source)
        else:
            tree = source # try just using it as dom

        self.unknown_tags = []
        self.unknown_types = []
        return self._dom2object(*tree.childNodes)

    def _dom2object(self, *nodes):
        """ transform dom-nodes to objects """
        res = Frag()
        for node in filter(None, nodes):
            if node.nodeType == node.ELEMENT_NODE:
                childs = self._dom2object(*node.childNodes)
                cls = self.typemap.get(node.nodeName)
                if not cls:
                    self.unknown_tags.append(node.nodeName)
                    res.extend(childs)
                else:
                    attrs = {}
                    if node.attributes:
                        for name, item in node.attributes.items():
                            attrs[name]=item # Text(item) # .nodeValue)
                    res.append(cls(attrs, *childs))

            elif node.nodeType == node.TEXT_NODE:
                res.append(self.typemap.get('Text', Text)(node.nodeValue))
            else:
                self.unknown_types.append(node.nodeType)
        return res
