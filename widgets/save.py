## Script (Python) "save"
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

context.save_helper()
context.invalidate_cache_helper()
return context.redirect()
