## Script (Python) "simple_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node
##title=
##
request = context.REQUEST
model = request.model
editorsupport = context.service_editorsupport

for child in node.childNodes:
    if child.nodeType == node.ELEMENT_NODE:
        break
    
supp = editorsupport.getMixedContentSupport(model, child)
return supp.renderEditable()
