## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# $Id: save_helper.py,v 1.1 2003/06/30 15:38:25 faassen Exp $
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

# don't need to convert it, will do so in replace_text later
data = request['data']

# strip off empty newlines at the end
data = data.rstrip()

if element_type not in ['normal', 'compact']:
    return

node.setAttribute('type', node.input_convert(element_type))

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
    editorsupport.replace_text(dt, pair[0])
    node.appendChild(dt)
    dd = doc.createElement('dd')
    if len(pair) > 1:
        editorsupport.replace_text(dd, '\n'.join(pair[1:]))
    else:
        editorsupport.replace_text(dd, '')
    node.appendChild(dd)
