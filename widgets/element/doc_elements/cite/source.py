

node = context.REQUEST.node
editorsupport = context.service_editorsupport
author = node.getAttribute('source')
if not author:
    return ''
return editorsupport.render_links(author)

