

node = context.REQUEST.node
editorsupport = context.service_editorsupport

html = []

for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName != 'p':
        continue
    html.append(editorsupport.render_text_as_html(child))

return html

