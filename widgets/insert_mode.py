## Script (Python) "insert_mode"
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

allowed_types = context.get_allowed_info(context.REQUEST.wr_name,node)
if len(allowed_types)==1:
   return context.insert(what = allowed_types[0][1])
else:
   context.service_editor.setNodeWidget(node, 
      context.get_widget_path()[:-1] + ('mode_insert',))
   return context.redirect()
