## Script (Python) "save_and_insert"
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

request = context.REQUEST

context.save_helper()
context.invalidate_cache_helper()

if request.has_key('element_switched'):
    return context.redirect()

context.done_mode()
return context.service_editor.getWidget(request.node).insert_mode()
