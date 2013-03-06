# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.SilvaExternalSources.ExternalSource import getSourceForId

def getSourceParameters(context, node):
    """ Extract parameter values for the external source from
    the Document's XML node.
    """
    parameters = {}
    for child in [child for child in node.childNodes
              if child.nodeType == child.ELEMENT_NODE
              and child.nodeName == 'parameter']:
        child.normalize()
        name = child.getAttribute('key').encode('ascii')
        type = child.getAttribute('type') or 'string'
        value = [child.nodeValue for child in child.childNodes
                 if child.nodeType == child.TEXT_NODE]
        value = ' '.join(value)
        # XXX currently we only treat type="list" in a different manner,
        # non-string values are ignored (not sure if they should be dealt with
        # too, actually)
        if type == 'list':
            # XXX evil eval, same in Formulator, though
            value = eval(value)
        elif type == 'boolean':
            try:
                value = int(value)
            except ValueError: #if it's not a number, assume false
                value = 0
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


