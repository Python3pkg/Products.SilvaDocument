request = context.REQUEST
model = request.model
node = request.node
id = node.getAttribute('id').encode('ascii')
service = context.service_editorsupport

return service.getSourceForId(model, id)