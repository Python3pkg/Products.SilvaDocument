## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
node = request.node
data = request['data']

model = node.get_content()

editorsupport = context.service_editorsupport
supp = editorsupport.getMixedContentSupport(model, node)
supp.parse(data)
