from Products.Silva.mangle import String

request = context.REQUEST
node = request.node
editorsupport = context.service_editorsupport

if request['what'] != 'p':
    context.element_switch()
    return

# don't need to convert this, later on we will convert it in replace_text()
data = request['data']
type = request['element_type']

# split into number of text items
lines = data.split('\r\n')
lines = [ line.strip() for line in lines ]
data = '\r\n'.join(lines)
items = data.split('\r\n\r\n')
# replace text in node
editorsupport.replace_text(node, items[0])
# if necessary, add new paragraphs
if len(items) > 1:
    doc = node.ownerDocument
    next = node.nextSibling
    for item in items[1:]:
        p = doc.createElement('p')
        editorsupport.replace_text(p, item)
        node.parentNode.insertBefore(p, next)

node.setAttribute('type', String.inputConvert(type))
