## Script (Python) "editable_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node_name
##title=
##
request = context.REQUEST
model = request.model
node = context.REQUEST.node
editorsupport = context.service_editorsupport
editable = []
for child in node.childNodes:
    if child.nodeType != child.ELEMENT_NODE:
        continue
    if child.nodeName != node_name:
        continue
    supp = editorsupport.getMixedContentSupport(model, child)
    editable.append(supp.renderEditable())

return context.service_editor.safeJoin('\r\n\r\n', editable)

