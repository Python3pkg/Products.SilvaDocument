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

texts = []
for child in node.childNodes:
    if child.nodeType == node.ELEMENT_NODE and child.nodeName == 'li':
        supp = editorsupport.getMixedContentSupport(model, child)
        texts.append(supp.renderHTML(view_type=view_type))
        
if node.hasAttribute('type'):
    type = node.getAttribute('type')
else:
    type = 'disc'
    
return context.util.render_list(type, texts)
