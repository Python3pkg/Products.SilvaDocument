# $Id: save_helper.py,v 1.3 2004/07/21 11:46:42 jw Exp $
from Products.Silva import mangle

request = context.REQUEST
node = request.node
doc = node.ownerDocument
editorsupport = context.service_editorsupport

model = node.get_content()

# node_name, editable, multiple paragraphs allowed
cite_elements = [
    ('author', request['author'], 0),
    ('source', request['source'], 0),
    ('p', request['citation'], 1),
    ]
    
while node.firstChild is not None:
    node.removeChild(node.firstChild)
    
for node_name, content, multiple in cite_elements:
    content = content.strip()
    if multiple:
        content = content.strip().split("\r\n\r\n")
    else:
        content = [content]
    for p in content:
        p_node = node.appendChild(doc.createElement(node_name))
        supp = editorsupport.getMixedContentSupport(model, p_node)
        supp.parse(p)
