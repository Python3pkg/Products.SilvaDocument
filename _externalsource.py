# This module contains code to integrate the SilvaExternalSources extension
# with the SilvaDocument extension.

from Products.SilvaDocument.externalsource import getSourceForId

def getSourceParameters(context, node):
    """ Extract parameter values for the external source from 
    the Document's XML node.
    """
    id = node.getAttribute('id').encode('ascii')
    parameters = {}        
    for child in [child for child in node.childNodes 
              if child.nodeType == child.ELEMENT_NODE 
              and child.nodeName == 'parameter']:
        child.normalize()
        name = child.getAttribute('key').encode('ascii')
        value = [child.nodeValue for child in child.childNodes 
                 if child.nodeType == child.TEXT_NODE]
        value = ' '.join(value)
        parameters[name] = value
    return parameters

def isSourceCacheable(context, node):
    """ Helps to see if the Document using an external source 
    defined in the XML node is cacheable.
    """
    id = node.getAttribute('id').encode('ascii')
    source = getSourceForId(context, id)
    if source is None:
        return 1
    parameters = getSourceParameters(context, node)
    is_cacheable = source.is_cacheable(**parameters)
    return is_cacheable
