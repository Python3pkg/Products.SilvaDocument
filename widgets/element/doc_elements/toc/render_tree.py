##parameters=model=None, toc_depth=-1, public=0, append_to_url=None

from Products.Silva.adapters import tocrendering

adapter = tocrendering.getTOCRenderingAdapter(model)
return adapter.render_tree(public, append_to_url, toc_depth)
