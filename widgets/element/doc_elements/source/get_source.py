from Products.SilvaExternalSources.ExternalSource import getSourceForId

request = context.REQUEST
node = request.node
id = node.getAttribute('id').encode('ascii')
# Use Document's context. If not, the complete widgets hierarchy comes
# in play and weird acquisition magic may cause 'source' to be a widget 
# whenever the source object has a widget's id.
doc = node.get_silva_object()
return getSourceForId(doc, id)