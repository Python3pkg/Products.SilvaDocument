## Script (Python) "text_editable_content"
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
editorsupport = context.service_editorsupport

supp = editorsupport.getMixedContentSupport(model, node)
return supp.renderEditable()
