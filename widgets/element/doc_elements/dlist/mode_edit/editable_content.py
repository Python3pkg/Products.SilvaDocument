## Script (Python) "editable_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
model = request.model
node = request.node
editorsupport = context.service_editorsupport

retval = ''
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    supp = editorsupport.getMixedContentSupport(model, child)
    retval += supp.renderEditable().strip()
    if child.nodeName == 'dt':
        retval += '\r\n'
    elif child.nodeName == 'dd':
        retval += '\r\n\r\n'

return retval
