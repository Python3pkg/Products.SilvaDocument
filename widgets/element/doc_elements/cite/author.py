

node = context.REQUEST.node
editorsupport = context.service_editorsupport
author = node.getAttribute('author')
if not author:
    return ''
return editorsupport.render_links(author)

