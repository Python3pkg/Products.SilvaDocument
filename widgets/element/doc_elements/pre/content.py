## Script (Python) "content"
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
editorsupport = model.service_editorsupport
view_type = (context.id == 'mode_view') and 'public' or 'edit'

supp = editorsupport.getMixedContentSupport(model, node)
return supp.renderHTML(view_type=view_type)