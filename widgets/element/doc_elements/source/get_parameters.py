request = context.REQUEST
node = request.node
parameters = {}

for child in [child for child in node.childNodes 
                 if child.nodeType == child.ELEMENT_NODE 
                     and child.nodeName == 'parameter']:
    child.normalize()
    name = child.getAttribute('key')
    value = [child.nodeValue for child in child.childNodes 
             if child.nodeType == child.TEXT_NODE]
    value = ' '.join(value)
    parameters[name] = value

return parameters
