## Script (Python) "editable_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node_name
##title=
##
node = context.REQUEST.node
editorsupport = context.service_editorsupport
editable = []
for child in node.childNodes:
    if child.nodeType != child.ELEMENT_NODE:
        continue
    if child.nodeName != node_name:
        continue
    editable.append(editorsupport.render_text_as_editable(child))

return '\r\n\r\n'.join(editable)

