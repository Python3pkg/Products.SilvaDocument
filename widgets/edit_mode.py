## Script (Python) "edit_mode"
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

context.edit_mode_helper()
return context.redirect()
