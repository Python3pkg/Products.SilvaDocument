request = context.REQUEST
node = request.node
path = node.getAttribute('path').encode('ascii')
datasource = None

if path:
    datasource = node.restrictedTraverse(path, None)

return datasource