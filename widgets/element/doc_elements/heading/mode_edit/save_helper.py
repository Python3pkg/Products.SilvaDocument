from Products.Silva.mangle import String

request = context.REQUEST
node = request.node
editor = context.service_editorsupport

model = node.get_content()

if request['what'] != 'heading':
    context.element_switch()
    return

data = request['data']
type = request['element_type']

supp = editor.getMixedContentSupport(model, node)
supp.parse(data)

# special case of element switching:
if getattr(request,'element_switched',None):
   title = getattr(request,'list_title', None)
   if title:
      doc = node.ownerDocument
      p = doc.createElement('heading')
      node.parentNode.insertBefore(p, node)
      supp = editor.getMixedContentSupport(model, p)
      supp.parse(title)

node.setAttribute('type', String.inputConvert(type))
