# $Id: save_helper.py,v 1.1 2003/10/28 11:58:39 zagy Exp $
from Products.Silva import mangle

request = context.REQUEST
node = request.node
editorsupport = context.service_editorsupport


author = mangle.String.inputConvert((request['author']))
source = mangle.String.inputConvert((request['source']))
citation = request['citation']

if author:
    node.setAttribute('author', author)
else:
    node.removeAttribute('author')
if source:
    node.setAttribute('source', source)
else:
    node.removeAttribute('source')

while node.firstChild is not None:
    node.removeChild(node.firstChild)
paragraphs = citation.strip().split("\r\n\r\n")
doc = node.ownerDocument
for paragraph in paragraphs:
    p_node = node.appendChild(doc.createElement('p'))
    p_node.setAttribute('type', 'normal')
    editorsupport.replace_text(p_node, paragraph)

