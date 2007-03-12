# This module contains code to integrate the SilvaExternalSources extension
# with the SilvaDocument extension.
from Products.SilvaExternalSources import ExternalSource

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
        type = child.getAttribute('type') or 'string'
        # XXX currently we only treat type="list" in a different manner, 
        # non-string values are ignored (not sure if they should be dealt with 
        # too, actually)
        if type == 'list':
            # XXX evil eval, same in Formulator, though
            value = eval(value)
        elif type == 'boolean':
            value = int(value)
        parameters[name] = value
    return parameters

def isSourceCacheable(context, node):
    """ Helps to see if the Document using an external source 
    defined in the XML node is cacheable.
    """
    id = node.getAttribute('id').encode('ascii')
    source = ExternalSource.getSourceForId(context, id)
    if source is None:
        return 1
    parameters = getSourceParameters(context, node)
    is_cacheable = source.is_cacheable(**parameters)
    return is_cacheable
