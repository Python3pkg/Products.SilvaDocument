# $Id: save_helper.py,v 1.3 2004/07/21 11:46:42 jw Exp $
from Products.Silva.mangle import String

request = context.REQUEST
node = request.node
model = node.get_content()
editorsupport = context.service_editorsupport

if request['what'] != 'dlist':
    context.element_switch()
    return

if not request.has_key('element_type'):
    element_type = 'normal'
else:
    element_type = request['element_type']

# strip off empty newlines at the end
data = request['data']
data = data.rstrip()

if element_type not in ['normal', 'compact']:
    return

node.setAttribute('type', String.inputConvert(element_type))

# remove previous items, except for the title node
childNodes = [ child 
    for child in  node.childNodes 
    if child.nodeName=='dd' or child.nodeName == 'dt']
childNodes.reverse()
for child in childNodes:
    node.removeChild(child)

# now add new items
doc = node.ownerDocument

# reduce multiple linebreaks to 2
while data.find('\r\n\r\n\r\n') > -1:
    data = data.replace('\r\n\r\n\r\n', '\r\n\r\n')

items = data.split('\r\n\r\n')
for item in items:
    pair = item.split('\r\n')
    dt = doc.createElement('dt')
    node.appendChild(dt)    
    supp = editorsupport.getMixedContentSupport(model, dt)
    supp.parse(pair[0])    
    dd = doc.createElement('dd')
    node.appendChild(dd)
    supp = editorsupport.getMixedContentSupport(model, dd)
    if len(pair) > 1:
        supp.parse('\n'.join(pair[1:]))
    else:
        supp.parse('')
