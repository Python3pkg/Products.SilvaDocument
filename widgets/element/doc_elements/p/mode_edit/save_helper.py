from Products.Silva.mangle import String

request = context.REQUEST
node = request.node
editorsupport = context.service_editorsupport

model = node.get_content()

if request['what'] != 'p':
    context.element_switch()
    return

data = request['data']
type = request['element_type']

# split into number of text items
lines = data.split('\r\n')
lines = [ line.strip() for line in lines ]
data = '\r\n'.join(lines)
items = data.split('\r\n\r\n')
# replace text in node
supp = editorsupport.getMixedContentSupport(model, node)
supp.parse(items[0])
# if necessary, add new paragraphs
if len(items) > 1:
    doc = node.ownerDocument
    next = node.nextSibling
    for item in items[1:]:
        p = doc.createElement('p')
        node.parentNode.insertBefore(p, next)
        supp = editorsupport.getMixedContentSupport(model, p)
        supp.parse(item)

node.setAttribute('type', String.inputConvert(type))
