request = context.REQUEST
node = request.node
id = node.getAttribute('id').encode('ascii')

return getattr(context, id, None)