## Script (Python) "save_and_exit"
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
if not request.has_key('element_switched'):
    context.done_mode() 
return context.redirect()
