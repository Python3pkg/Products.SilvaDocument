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

supp = editorsupport.getMixedContentSupport(model, node)
return supp.renderHTML(view_type='public')