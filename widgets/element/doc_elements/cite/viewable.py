##parameters=element_name

request = context.REQUEST
model = request.model
node = context.REQUEST.node
editorsupport = context.service_editorsupport

elements = node.getElementsByTagName(element_name)
if not elements:
    return ''

viewable = []
view_type = (context.id == 'mode_view') and 'public' or 'edit'
for element in elements:
    supp = editorsupport.getMixedContentSupport(model, element)
    viewable.append(supp.renderHTML(view_type=view_type))

return viewable
