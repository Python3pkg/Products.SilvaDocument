request = context.REQUEST
model = request.model
service = context.service_editorsupport

ctxt = model.get_container()

sources = []
for id, source in service.availableSources(ctxt):
    sources.append(source)

sources.sort(lambda s1, s2: cmp(s1.title, s2.title))
return sources