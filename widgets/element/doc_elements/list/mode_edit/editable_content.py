## Script (Python) "editable_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
import string

request = context.REQUEST
model = request.model
node = request.node
editorsupport = context.service_editorsupport

items = []
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'li':
        supp = editorsupport.getMixedContentSupport(model, child)
        items.append(supp.renderEditable())

items = map(string.strip, items)
return '\r\n\r\n'.join(items)
