content = context.REQUEST.model
version = content.get_viewable()
if version is None:
    return  'Sorry, this Silva Document is not viewable.'
version.render_view()
