## Script (Python) "delete"
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

context.service_editor.clearNodeWidget(node)
context.invalidate_cache_helper()

node.parentNode.removeChild(node)
return context.redirect()
