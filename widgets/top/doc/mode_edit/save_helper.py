from Products.Silva.mangle import String

request = context.REQUEST
node = request.node
document = node.get_content()
data = String.inputConvert(request['data'])
document.set_title(data)
