# $Id: save_helper.py,v 1.2 2003/11/08 13:04:32 zagy Exp $
from Products.Silva import mangle

request = context.REQUEST
node = request.node
doc = node.ownerDocument
editorsupport = context.service_editorsupport

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
        editorsupport.replace_text(p_node, p)

