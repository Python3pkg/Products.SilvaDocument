from Products.SilvaExternalSources.ExternalSource import availableSources

request = context.REQUEST
ctxt = request.model.get_container()

sources = []
for id, source in availableSources(ctxt):
    sources.append(source)

sources.sort(lambda s1, s2: cmp(s1.title, s2.title))
return sources