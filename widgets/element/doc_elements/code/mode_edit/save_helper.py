from Products.Silva.mangle import String

request = context.REQUEST
node = request.node
if request.has_key('path'):
    path = request['path']
else:
    path = '' 
node.setAttribute('path', String.inputConvert(path))
