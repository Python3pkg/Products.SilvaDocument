from Products.Silva.mangle import String

request = context.REQUEST
node = request.node

toc_depth = request['toc_depth']
node.setAttribute('toc_depth', String.inputConvert(toc_depth))
