node = context.REQUEST.node
path = node.getAttribute('path')
if path:
    return node.restrictedTraverse(path.encode('ascii', 'ignore'), None)
