## Script (Python) "move_up"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if not context.check_editable():
    return context.redirect()

node = context.REQUEST.node

n = node
while 1:
    n = n.previousSibling
    if n is None or n.nodeType == node.ELEMENT_NODE:
        break
# can't go further up, so stop
if n is None:
    return

parent = node.parentNode
#parent.removeChild(node)
parent.insertBefore(node, n)
context.service_editor.setNodeWidget(node,
   context.get_widget_path()[:-1] + ('mode_done',))
return context.redirect()
