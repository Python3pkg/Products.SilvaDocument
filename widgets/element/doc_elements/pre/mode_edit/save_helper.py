## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
editorsupport = context.service_editorsupport
request = context.REQUEST
node = request.node

model = node.get_content()

if request['what'] != 'pre':
    context.element_switch()
    return

data = request['data']
supp = editorsupport.getMixedContentSupport(model, node)
supp.parse(data)
