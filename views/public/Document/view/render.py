version = context.REQUEST.model
node = version.content.documentElement
context.service_editor.setViewer('service_doc_viewer')
return context.service_editor.renderView(node)
