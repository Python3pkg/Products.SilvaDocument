from Products.Silva.mangle import String

request = context.REQUEST
node = request.node
editor = context.service_editorsupport

if request['what'] != 'heading':
    context.element_switch()
    return

data = request['data']
type = request['element_type']

editor.replace_heading(node, data)

# special case of element switching:
if getattr(request,'element_switched',None):
   title = getattr(request,'list_title', None)
   if title:
      doc = node.ownerDocument
      p = doc.createElement('heading')
      editor.replace_heading(p, title)
      node.parentNode.insertBefore(p, node)

node.setAttribute('type', String.inputConvert(type))
