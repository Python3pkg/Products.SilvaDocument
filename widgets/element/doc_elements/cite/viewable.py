##parameters=element_name

node = context.REQUEST.node
editorsupport = context.service_editorsupport
show_index = context.show_index()

elements = node.getElementsByTagName(element_name)
if not elements:
    return ''
viewable = []
for element in elements:
    viewable.append(editorsupport.render_text_as_html(element, show_index))
return viewable

