request = context.REQUEST
model = request.model
node = request.node
service = context.service_editorsupport

return service.getSourceParameters(model, node)
